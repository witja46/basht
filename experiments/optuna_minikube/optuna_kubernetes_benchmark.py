import random
from os import path
from time import sleep

import optuna
from kubernetes import client, config, utils, watch
from kubernetes.utils import create_from_yaml
from ml_benchmark.benchmark_runner import Benchmark
from ml_benchmark.utils.image_build_wrapper import MinikubeImageBuilder
from ml_benchmark.workload.mnist.mnist_task import MnistTask

config.load_kube_config()


class OptunaMinikubeBenchmark(Benchmark):

    def __init__(self, resources) -> None:
        self.resources = resources
        self.namespace = f"optuna-study-{random.randint(0, 10024)}"
        self.image_builder = MinikubeImageBuilder()
        self.master_ip = self.image_builder.get_url()

    def deploy(self) -> None:
        """
        Deploy DB
        """

        client.CoreV1Api().create_namespace(client.V1Namespace(metadata=client.V1ObjectMeta(name=self.namespace)))

        k8s_beta = client.ApiClient()
        resp = create_from_yaml(k8s_beta, path.join(path.dirname(__file__),"ops/manifests/db/db-deployment.yml"), namespace=self.namespace, verbose=True)
        print("Deployment created. status='%s'" % str(resp))

        # wait for DB to be ready
        # w = watch.Watch()
        # for event in w.stream(client.CoreV1Api().list_namespaced_service,
        # namespace=self.namespace,
        # _request_timeout=60):
        #     if event["object"].metadata.name == "postgres" and event["object"].status.phase == "Running":
        #         w.stop()
        #         return

    def setup(self):
        """

        """
        self.trial_tag = "optuna-trial:latest"
        logs = self.image_builder.deploy_image(path.join(path.dirname(__file__), "dockerfile.trial"), self.trial_tag)
        print(f"Image: {self.trial_tag}")
        for line in logs:
            print(line)

    def run(self):
        """Start Trial Containers in Subprocesses
        """
        # deploy
        file_path = path.join(path.dirname(__file__), "ops/manifests/trial/deployment.yml")
        k8s_beta = client.ApiClient()
        resp = create_from_yaml(k8s_beta, file_path, namespace=self.namespace, verbose=True)
        print("Deployment created. status='%s'" % str(resp))

    def getDBUrl(self):
        cmd = client.CoreV1Api()
        postgres_sepc = cmd.read_namespaced_service(namespace=self.namespace, name="postgres")
        if postgres_sepc is not None:
            if len(postgres_sepc.spec.ports) > 0 and postgres_sepc.spec.ports[0].node_port > 0:
                #XXX: hardcoded credentaials - should match ops/mainifests/db/db-deployment.yaml#ostgres-config
                url = f"postgresql://postgresadmin:admin123@{self.master_ip}:{postgres_sepc.spec.ports[0].node_port}/postgresdb"
                print(url)
                return url
            raise Exception("Postgres DB not found - spec dose not have node port}"+str(postgres_sepc))
        raise Exception("Postgres DB URL not found")

    def collect_run_results(self):
        """Collect results form container or on master?
        """
        sleep(10)
        study = optuna.load_study(study_name="optuna_study", storage=self.getDBUrl())
        study.get_trials()
        self.best_trial = study.best_trial

    def test(self):

        def optuna_trial(trial):
            objective = MnistTask(config_init={"epochs": 1}).create_objective()
            lr = trial.suggest_float("learning_rate", 1e-3, 0.1, log=True)
            decay = trial.suggest_float("weight_decay", 1e-6, 1e-4, log=True)
            objective.set_hyperparameters({"learning_rate": lr, "weight_decay": decay})
            # these are the results, that can be used for the hyperparameter search
            objective.train()
            validation_scores = objective.validate()
            return validation_scores["macro avg"]["f1-score"]

        self.scores = optuna_trial(self.best_trial)

    def collect_benchmark_metrics(self):
        results = dict(
            test_scores=self.scores
            )
        return results

    def undeploy(self):
        """Kill all containers
        """
        cmd = client.CoreV1Api()
        #cmd.delete_namespace(self.namespace)


if __name__ == "__main__":

    from ml_benchmark.benchmark_runner import BenchmarkRunner
    from ray import tune

    # The basic config for the workload. For testing purposes set epochs to one.
    # For benchmarking take the default value of 100
    # your ressources the optimization should run on
    resources = {"cpu": 12}

    # Add your hyperparameter setting procedure here
    # your hyperparameter grid you want to search over
    hyperparameters = dict(
            input_size=28*28, learning_rate=tune.grid_search([1e-4]),
            weight_decay=1e-6,
            hidden_layer_config=tune.grid_search([[20], [10, 10]]),
            output_size=10)

    # import an use the runner
    runner = BenchmarkRunner(
        benchmark_cls=OptunaMinikubeBenchmark, resources=resources)
    runner.run()
