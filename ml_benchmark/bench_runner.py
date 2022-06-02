import base64
import json
import datetime

from ml_benchmark.workload.mnist.mnist_task import MnistTask
from ml_benchmark.metrics import Metrics


class BenchmarkRunner():
    task_registry = {"mnist": MnistTask}

    def __init__(self, bench_name: str, config: dict, task_str: str, grid: dict, resources: dict) -> None:
        """
            benchName: uniqueName of the bechmark, used in logging
            config: configuration object
        """

        self.bench_name = bench_name
        # generate a unique name from the config
        base64_bytes = base64.b64encode(json.dumps(config).encode('ascii'))
        self.config_name = str(base64_bytes, 'ascii')

        self.rundate = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        # perpare logger
        self.logger = Metrics([self.bench_name, self.config_name, self.rundate], ["name", "config", "date"])

        # objective set up
        task = self.task_registry.get(task_str)()
        train_loader, val_loader, test_loader = task.create_data_loader(config)
        self.objective = task.objective_cls(
            epochs=config["epochs"],
            train_loader=train_loader, val_loader=val_loader, test_loader=test_loader)

        # hyperparameter adding
        grid["input_size"] = task.input_size
        grid["output_size"] = task.output_size
        self.grid = grid
        self.resources = resources

    def deploy(self) -> None:
        """
            With the completion of this step the desired architecture of the HPO Framework should be running
            on a platform, e.g,. in the case of Kubernetes it referes to the steps nassary to deploy all pods
            and services in kubernetes.
        """
        pass

    def setup(self, *args, **kwargs):
        """
        Every Operation that is needed before the actual optimization (trial) starts and that is not relevant
        for starting up workers or the necessary architecture.
        """

    def run(self, *args, **kwargs):
        """
            Executing the hyperparameter optimization on the deployed platfrom.
            use the metrics object to collect and store all measurments on the workers.
        """
        pass

    def collect_trial_results(self, *args, **kwargs):
        """
        This step collects all necessary results from all performed trials. Necessary results are results that
        are used in order to retrieve the best hyperparameter setting and to collect benchmark metrics.
        """

    def test(self, *args, **kwargs):
        """
        This step tests the model instantiated with the best hyperparameter setting on the test split of the
        provided task.
        """
        pass

    def collect_benchmark_metrics(self, *args, **kwargs):
        """
            Describes the collection of all gathered metrics, which are not used by the HPO framework
            (Latencies, CPU Resources, etc.). This step runs outside of the HPO Framework.
            Ensure to optain all metrics loggs and combine into the metrics object.
        """
        pass

    def undeploy(self, *args, **kwargs):
        """
            The clean-up procedure to undeploy all components of the HPO Framework that were deployed in the
            Deploy step.
        """
        pass

    def main(self, fname: str):
        self.logger.run_start = datetime.now()
        self.deploy()
        self.logger.setup_start = datetime.now()
        self.run(self.logger)
        self.logger.run_end = datetime.now()

        self.logger.resultcollection_start = datetime.now()
        self.collectMetrics()
        self.logger.resultcollection_end = datetime.now()
        self.undeploy()
        self.logger.undeploy_end = datetime.now()

        if fname is not None:
            self.logger.store(fname)
