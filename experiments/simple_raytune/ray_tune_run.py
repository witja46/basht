from ray import tune

from ml_benchmark.bench_runner import BenchmarkRunner


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

    def run(self):
        """
            Executing the hyperparameter optimization on the deployed platfrom.
            use the metrics object to collect and store all measurments on the workers.
        """
        def raytune_func(config):
            """The function for training and validation, that is used for hyperparameter optimization.
            Beware Ray Synchronisation: https://docs.ray.io/en/latest/tune/user-guide.html

            Args:
                config ([type]): [description]
            """
            objective = config.get("objective")
            hyperparameters = config.get("hyperparameters")
            device = config.get("device")
            objective.set_device(device)
            objective.set_hyperparameters(hyperparameters)
            # these are the results, that can be used for the hyperparameter search
            objective.train()
            validation_scores = objective.validate()
            tune.report(macro_f1_score=validation_scores["macro avg"]["f1-score"])

        analysis = tune.run(
            raytune_func,
            config=dict(
                objective=self.objective,
                hyperparameters=self.grid,
                device=self.resources["device"]
                ),
            sync_config=tune.SyncConfig(
                syncer=None  # Disable syncing
                ),
            local_dir="/tmp/ray_results",
            resources_per_trial={"cpu": 12, "gpu": 1 if self.resources["device"] else 0}
        )

        return analysis

    def collect_trial_results(self):
        self.best_config = self.analysis.get_best_config(metric="macro_f1_score", mode="max")["hyperparameters"]

    def test(self):
        # evaluating and retrieving the best model to generate test results.
        self.objective.set_device(self.resources["device"])
        self.objective.set_hyperparameters(self.best_config)
        self.training_loss = self.objective.train()
        self.test_scores = self.objective.test()

    def collect_benchmark_metrics(self):
        """
            Describes the collection of all gathered metrics, which are not used by the HPO framework (Latencies, CPU Resources, etc.). This step runs outside of the HPO Framework.
            Ensure to optain all metrics loggs and combine into the metrics object.
        """
        results = dict(
            test_scores=self.test_scores,
            training_loss=self.training_loss
            )

        # TODO: saving has to be adjusted
        saver = ResultSaver(
        experiment_name="GridSearch_MLP_MNIST", experiment_path=os.path.abspath(os.path.dirname(__file__)))
        saver.save_results(results)

    def undeploy(self):
        """
            The clean-up procedure to undeploy all components of the HPO Framework that were deployed in the Deploy step.
        """
        pass
