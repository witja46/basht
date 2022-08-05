import datetime

from prometheus_api_client import PrometheusConnect

from ml_benchmark.config import MetricsStorageConfig
import psycopg2
from sqlalchemy import MetaData, Table, create_engine, insert
from threading import Timer

from ml_benchmark.metrics import NodeUsage
import logging


class RepeatTimer(Timer):

    def run(self):
        while not self.finished.wait(self.interval):
            self.function(*self.args, **self.kwargs)


def _sum_samples(samples):
    return sum(map(lambda x: x.value, samples))


class ResourceTracker:

    # update every 2 seconds ... maybe make this tuneable
    UPDATE_INTERVAL = 2

    def __init__(self, prometheus_url):
        if prometheus_url is None:
            raise ValueError("Prometheus URL is required.")
        self.prometheus_url = prometheus_url
        self.prm = PrometheusConnect(url=self.prometheus_url, disable_ssl=True)

        if not self.prm.check_prometheus_connection():
            raise ValueError("Could not connect to Prometheus.")

        self.engine = self._create_engine()
        self.timer = RepeatTimer(self.UPDATE_INTERVAL, self.update)

        self._check_metrics()

    def _check_metrics(self):
        available = set(self.prm.all_metrics())

        #check node_exporter metrics - cpu/memory
        required = {"node_memory_MemFree_bytes", "node_memory_MemTotal_bytes", "node_cpu_seconds_total"}
        if not required.issubset(available):
            raise ValueError("Prometheus does not provide the required metrics.")

        #check if prometheus is managing a kubernetes cluster
        if "container_network_transmit_bytes_total" in available:
            self.network_metric = "container_network"
        elif "node_network_transmit_bytes_total" in available:
            self.network_metric = "node_network"
        else:
            raise ValueError("Prometheus does not provide a vaild network metric.")

        if "kube_node_info" in available:
            info = self.prm.get_current_metric_value("kube_node_info")
            self.node_map = dict(map(lambda x: (x["internal_ip"], x["node"]), map(lambda x: x["metric"], info)))
        else:
            self.node_map = {}

    def _create_engine(self):
        try:
            engine = create_engine(MetricsStorageConfig.connection_string, echo=True)
        except psycopg2.Error:
            raise ConnectionError("Could not create an Engine for the Postgres DB.")
        return engine

    def update(self):
        try:
            self.track()
        except Exception as e:
            logging.exception("Error while updating resource tracker. %s", e)

    def track(self):
        #query prometheus for node usage
        memory = 'avg by (instance) (node_memory_MemFree_bytes/node_memory_MemTotal_bytes)'
        cpu = '100 - (avg by (instance) (irate(node_cpu_seconds_total{mode="idle"}[2m])*100))'
        network = f'sum by (instance) (rate({self.network_metric}_receive_bytes_total[2m])+rate({self.network_metric}_transmit_bytes_total[2m]))'

        mem_result = self.prm.custom_query(memory)
        cpu_result = self.prm.custom_query(cpu)
        network_result = self.prm.custom_query(network)

        logging.debug("Got results from Prometheus.", mem_result, cpu_result, network_result)

        # assert len(mem_result) == len(cpu_result) == len(network_result)

        #grab the data per instance
        mem_result = dict(map(lambda x: (self._try_norm(x["metric"]["instance"]), float(x["value"][1])), mem_result))
        cpu_result = dict(map(lambda x: (self._try_norm(x["metric"]["instance"]), float(x["value"][1])), cpu_result))
        network_result = dict(map(lambda x: (self._try_norm(x["metric"]["instance"]), float(x["value"][1])), network_result))

        logging.debug("Processed Prometheus Results", mem_result, cpu_result, network_result)

        # assert mem_result.keys() == cpu_result.keys() == network_result.keys()

        #merge the data
        data = []
        for instance in mem_result:
            n = NodeUsage(instance)
            n.timestamp = datetime.datetime.now()
            n.cpu_usage = cpu_result.get(instance, 0)
            n.memory_usage = mem_result.get(instance, 0)
            n.network_usage = network_result.get(instance, 0)
            data.append(n)
            logging.debug("Added node usage for %s", instance)

        #insert the data
        for n in data:
            metadata = MetaData(bind=self.engine)
            node_usage = Table("resources", metadata, autoload_with=self.engine)
            with self.engine.connect() as conn:
                stmt = insert(node_usage).values(n.to_dict())
                conn.execute(stmt)

    def _try_norm(self, instance: str):
        if instance in self.node_map:
            return self.node_map[instance]
        elif instance[:instance.find(":")] in self.node_map:
            return self.node_map[instance[:instance.find(":")]]
        else:
            return instance

    def start(self):
        logging.debug("Starting resource tracker.")
        self.timer.start()

    def stop(self):
        logging.debug("Stopping resource tracker.")
        self.timer.cancel()
