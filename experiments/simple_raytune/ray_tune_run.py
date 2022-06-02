from ray import tune

from ml_benchmark.bench_runner import BenchmarkRunner
from ml_benchmark.workload.mnist.mnist_task import MnistTask
from ml_benchmark.workload.mnist.mlp_objective import MLPObjective


class RaytuneRun(BenchmarkRunner):

    def __init__(self, benchName, config) -> None:
        super().__init__(benchName, config)

    def deploy(self) -> None:
        """
            With the completion of this step the desired architecture of the HPO Framework should be running on a platform, e.g,. in the case of Kubernetes it referes to the steps nassary to deploy all pods and services in kubernetes.
        """
        pass

    def setup(self):
        pass

    def run(self,m:Metrics) -> str:
        """
            Executing the hyperparameter optimization on the deployed platfrom.
            use the metrics object to collect and store all measurments on the workers.
        """
        analysis = tune.run(
        raytune_func,
            config=dict(
                objective=self.objective,
                hyperparameters=hyperparameters,
                device=resources["device"]
                ),
            sync_config=tune.SyncConfig(
                syncer=None  # Disable syncing
                ),
            local_dir="/tmp/ray_results",
            resources_per_trial={"cpu": 12, "gpu": 1 if resources["device"] else 0}
        )

    def collect_benchmark_metrics(self):
        """
            Describes the collection of all gathered metrics, which are not used by the HPO framework (Latencies, CPU Resources, etc.). This step runs outside of the HPO Framework.
            Ensure to optain all metrics loggs and combine into the metrics object.
        """
        results = dict(
        execution_time=time.time() - start_time,
        test_scores=test_scores,
        training_loss=training_loss
            )
        saver = ResultSaver(
        experiment_name="GridSearch_MLP_MNIST", experiment_path=os.path.abspath(os.path.dirname(__file__)))
        saver.save_results(results)

    def undeploy(self):
        """
            The clean-up procedure to undeploy all components of the HPO Framework that were deployed in the Deploy step.
        """
        pass

    def test(self):
        # evaluating and retrieving the best model to generate test results.
        objective.set_device(device)
        objective.set_hyperparameters(best_config)
        training_loss = objective.train()
        test_scores = objective.test()


    def collect_trial_results(self):
        self.best_config = analysis.get_best_config(metric="macro_f1_score", mode="max")["hyperparameters"]
