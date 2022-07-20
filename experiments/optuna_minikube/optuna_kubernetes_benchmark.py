import random
from os import path
import subprocess
from time import sleep

import optuna
from kubernetes import client, config, utils, watch
from kubernetes.utils import create_from_yaml
from ml_benchmark.benchmark_runner import Benchmark
from ml_benchmark.config import Path
from ml_benchmark.utils.image_build_wrapper import MinikubeImageBuilder
from ml_benchmark.workload.mnist.mnist_task import MnistTask

class OptunaMinikubeBenchmark(Benchmark):

    def __init__(self, resources) -> None:
        self.resources = resources
        self.namespace = f"optuna-study"#-{random.randint(0, 10024)}"
        
        #set up the image builder
        if "dockerImageBuilder" in self.resources:
            self.image_builder = self.resources["dockerImageBuilder"]
        else:
            self.image_builder = MinikubeImageBuilder()

        #ensures that we can work with kubernetes
        #TODO: if this fails we woun't know about it until we try to run the experiment...
        if "kubernetsContext" in self.resources:
            config.load_kube_config(context=self.resources["kubernetsContext"])
        else:
            config.load_kube_config()

        self.master_ip = subprocess.check_output("minikube ip", shell=True).decode("utf-8").strip("\n")

    def deploy(self) -> None:
        """
        Deploy DB
        """
        #TODO: deal with exsiting resources...
        client.CoreV1Api().create_namespace(client.V1Namespace(metadata=client.V1ObjectMeta(name=self.namespace)))
        resp = create_from_yaml(client.ApiClient(), path.join(path.dirname(__file__),"ops/manifests/db/db-deployment.yml"), namespace=self.namespace, verbose=True)
        print("Deployment created. status='%s'" % str(resp))

    def setup(self):
        """

        """
        self.trial_tag = "optuna-trial:latest"
        logs = self.image_builder.deploy_image("experiments/optuna_minikube/dockerfile.trial", self.trial_tag, Path.root_path)
        print(f"Image: {self.trial_tag}")
        for line in logs:
            print(line)

    def run(self):
        """Start Trial Containers in Subprocesses
        """
        # deploy
        file_path = path.join(path.dirname(__file__), "ops/manifests/trial/job.yml")
        resp = create_from_yaml(client.ApiClient(), file_path, namespace=self.namespace, verbose=True)
        print("Deployment created. status='%s'" % str(resp))

    def getDBUrl(self):
        cmd = client.CoreV1Api()
        postgres_sepc = cmd.read_namespaced_service(namespace=self.namespace, name="postgres")
        if postgres_sepc is not None:
            if len(postgres_sepc.spec.ports) > 0 and postgres_sepc.spec.ports[0].node_port > 0:
                # XXX: hardcoded credentaials - should match ops/mainifests/db/db-deployment.yaml#ostgres-config
                url = f"postgresql://postgresadmin:admin123@{self.master_ip}:{postgres_sepc.spec.ports[0].node_port}/postgresdb"
                return url
            raise Exception("Postgres DB not found - spec dose not have node port}"+str(postgres_sepc))
        raise Exception("Postgres DB URL not found")

    def collect_run_results(self):
        """Collect results form container or on master?
        """
        self._watch_trials()
        study = optuna.load_study(study_name="optuna_study", storage=self.getDBUrl())
        self.best_trial = study.best_trial

    def _watch_trials(self):
        w = watch.Watch()
        c = client.BatchV1Api()
        for e in w.stream(c.list_namespaced_job, namespace=self.namespace, timeout_seconds=10):
            if "object" in e and e["object"].status.completion_time is not None:
                w.stop()
                return

        print("Trials completed! Collecting Results")

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
        client.CoreV1Api().delete_namespace(self.namespace)
        self.image_builder.cleanup(self.trial_tag)


if __name__ == "__main__":

    from ml_benchmark.benchmark_runner import BenchmarkRunner
    from ray import tune

    # The basic config for the workload. For testing purposes set epochs to one.
    # For benchmarking take the default value of 100
    # your ressources the optimization should run on
    resources = {
        "cpu": 12, # TODO: this doesnt work
        "dockerImageBuilder": MinikubeImageBuilder(),
        "kubernetesContext": "minikube",
    } 

    #TODO: hyperparams.

    # import an use the runner
    runner = BenchmarkRunner(
        benchmark_cls=OptunaMinikubeBenchmark, resources=resources)
    runner.run()
