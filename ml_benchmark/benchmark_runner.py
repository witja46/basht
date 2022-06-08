import base64
import json
from datetime import datetime
from abc import ABC, abstractmethod

from ml_benchmark.workload.mnist.mnist_task import MnistTask
from ml_benchmark.metrics import Metrics


class Benchmark(ABC):

    objective = None
    grid = None
    resources = None
    benchmark_path = None

    @abstractmethod
    def deploy(self) -> None:
        """
            With the completion of this step the desired architecture of the HPO Framework should be running
            on a platform, e.g,. in the case of Kubernetes it referes to the steps nassary to deploy all pods
            and services in kubernetes.
        """
        pass

    @abstractmethod
    def setup(self, *args, **kwargs):
        """
        Every Operation that is needed before the actual optimization (trial) starts and that is not relevant
        for starting up workers or the necessary architecture.
        """
        pass

    @abstractmethod
    def run(self, *args, **kwargs):
        """
            Executing the hyperparameter optimization on the deployed platfrom.
            use the metrics object to collect and store all measurments on the workers.
        """
        pass

    @abstractmethod
    def collect_trial_results(self, *args, **kwargs):
        """
        This step collects all necessary results from all performed trials. Necessary results are results that
        are used in order to retrieve the best hyperparameter setting and to collect benchmark metrics.
        """
        pass

    @abstractmethod
    def test(self, *args, **kwargs):
        """
        This step tests the model instantiated with the best hyperparameter setting on the test split of the
        provided task.
        """
        pass

    @abstractmethod
    def collect_benchmark_metrics(self, *args, **kwargs):
        """
            Describes the collection of all gathered metrics, which are not used by the HPO framework
            (Latencies, CPU Resources, etc.). This step runs outside of the HPO Framework.
            Ensure to optain all metrics loggs and combine into the metrics object.
        """
        pass

    @abstractmethod
    def undeploy(self, *args, **kwargs):
        """
            The clean-up procedure to undeploy all components of the HPO Framework that were deployed in the
            Deploy step.
        """
        pass


class BenchmarkRunner():
    task_registry = {"mnist": MnistTask}

    def __init__(
            self, benchmark_cls: Benchmark, config: dict, grid: dict,
            resources: dict, task_str: str = "mnist",) -> None:
        # TODO: set seed
        """
            benchName: uniqueName of the bechmark, used in logging
            config: configuration object
        """

        # generate a unique name from the config
        base64_bytes = base64.b64encode(json.dumps(config).encode('ascii'))
        self.config_name = str(base64_bytes, 'ascii')
        self.rundate = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        # setup benchmark
        task = self.task_registry.get(task_str)()
        epochs = config.pop("epochs")
        train_loader, val_loader, test_loader = task.create_data_loader(**config)
        objective = task.objective_cls(
            epochs=epochs,
            train_loader=train_loader, val_loader=val_loader, test_loader=test_loader)

        grid["input_size"] = task.input_size
        grid["output_size"] = task.output_size
        grid = grid
        resources = resources
        self.benchmark = benchmark_cls(objective, grid, resources)

        self.bench_name = f"{task.__class__.__name__}__{self.benchmark.__class__.__name__}"

        # set seeds
        self._set_all_seeds()

        # perpare logger
        self.logger = Metrics([self.bench_name, self.config_name, self.rundate], ["name", "config", "date"])
        # TODO: add maximum available resources??

    def run(self):
        self.logger.run_start = datetime.now()
        self.benchmark.deploy()
        self.logger.setup_start = datetime.now()
        self.benchmark.run()
        self.logger.run_end = datetime.now()
        self.logger.setup_start = datetime.now()
        self.benchmark.collect_trial_results()
        self.logger.run_end = datetime.now()
        self.logger.setup_start = datetime.now()
        self.benchmark.test()
        self.logger.run_end = datetime.now()
        self.logger.resultcollection_start = datetime.now()
        self.benchmark.collect_benchmark_metrics()
        self.logger.resultcollection_end = datetime.now()
        self.benchmark.undeploy()
        self.logger.undeploy_end = datetime.now()

    def _set_all_seeds(self):
        pass
