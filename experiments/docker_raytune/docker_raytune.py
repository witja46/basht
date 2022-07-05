from ml_benchmark.benchmark_runner import Benchmark
import docker


class RaytuneBenchmark(Benchmark):

    def __init__(self, objective, grid, resources) -> None:
        self.objective = objective
        self.grid = grid
        self.resources = resources

    def deploy(self) -> None:
        """
        Nothing to deploy as it just is docker.
        """
        pass

    def setup(self):
        """
        Create subpreocesses? Start Volumes?
        """
        self.trial_tag = "trial:latest"
        self.test_tag = "test:latest"

        self.client = docker.client.from_env()
        trial_image, logs = self.client.images.build("./dockerfile.trial")
        trial_image.tag = self.trial_tag
        print(f"Image: {self.trial_tag}")
        for line in logs:
            print(line)
        test_image, logs = self.client.images.build("./dockerfile.test")
        test_image.tag = self.test_tag
        print(f"Image: {self.test_tag}")
        for line in logs:
            print(line)

    def run(self):
        """Start Trial Containers in Subprocesses
        """
        # use multiprocessing to start multiple
        self.client.containers.run(self.trial_tag)

    def collect_run_results(self):
        """Collect results form container or on master?
        """

    def test(self):
        """Run test container?
        """

    def collect_benchmark_metrics(self):
        pass

    def undeploy(self):
        """Kill all containers
        """
        pass


if __name__ == "__main__":
    from ml_benchmark.config import MnistConfig
    from ml_benchmark.benchmark_runner import BenchmarkRunner
    from ray import tune

    # The basic config for the workload. For testing purposes set epochs to one.
    # For benchmarking take the default value of 100
    config = MnistConfig(epochs=1).to_dict()

    # your ressources the optimization should run on
    resources = {"cpu": 2}

    # Add your hyperparameter setting procedure here
    # your hyperparameter grid you want to search over
    hyperparameters = dict(
            input_size=28*28, learning_rate=tune.grid_search([1e-4]),
            weight_decay=1e-6,
            hidden_layer_config=tune.grid_search([[20], [10, 10]]),
            output_size=10)

    # import an use the runner
    runner = BenchmarkRunner(
        benchmark_cls=RaytuneBenchmark, config=config, grid=hyperparameters, resources=resources,
        task_str="mnist")
    runner.run()

