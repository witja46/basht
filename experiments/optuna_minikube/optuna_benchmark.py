import random
from os import path
import subprocess
from time import sleep
from colorlog import exception

import optuna
from kubernetes import client, config, utils, watch
from kubernetes.client import ApiException
from kubernetes.utils import create_from_yaml, FailToCreateError
import yaml
from ml_benchmark.benchmark_runner import Benchmark
from ml_benchmark.config import Path
from ml_benchmark.utils.image_build_wrapper import MinikubeImageBuilder, builder_from_string
from ml_benchmark.workload.mnist.mnist_task import MnistTask

from string import Template


class OptunaMinikubeBenchmark(Benchmark):


    def __init__(self, resources) -> None:
        self.resources = resources
        if "kubernetesNamespace" in resources:
            self.namespace = resources["kubernetesNamespace"]
        else:
            self.namespace = f"optuna-study-{random.randint(0, 10024)}"

        # set up the image builder
        if "dockerImageBuilder" in self.resources:
            self.image_builder = builder_from_string(self.resources["dockerImageBuilder"])
        else:
            self.image_builder = MinikubeImageBuilder()

        # ensures that we can work with kubernetes
        # TODO: if this fails we woun't know about it until we try to run the experiment...
        if "kubernetesContext" in self.resources:
            config.load_kube_config(context=self.resources["kubernetesContext"])
        else:
            config.load_kube_config()

        self.master_ip = resources["kubernetesMasterIP"]

        if "dockerImageTag" in self.resources:
            self.trial_tag = self.resources["dockerImageTag"]
        else:
            self.trial_tag = "optuna-trial:latest"

        if "studyName" in self.resources:
            self.study_name = self.resources["studyName"]
        else:
            self.study_name = "optuna-study"

        if "workerCpu" in self.resources:
            self.workerCpu = self.resources["workerCpu"]
        else:
            self.workerCpu = 2

        if "workerMemory" in resources:
            self.workerMemory = self.resources["workerMemory"]
        else:
            self.workerMemory = 2

        if "workerCount" in resources:
            self.workerCount = self.resources["workerCount"]
        else:
            self.workerCount = 4

        self.delete_after_run = self.resources["deleteAfterRun"] if "deleteAfterRun" in self.resources else True

    def deploy(self) -> None:
        """
        Deploy DB
        """
        # TODO: deal with exsiting resources...
        try:
            resp = client.CoreV1Api().create_namespace(
                client.V1Namespace(metadata=client.V1ObjectMeta(name=self.namespace)))
            print("Namespace created. status='%s'" % str(resp))
        except ApiException as e:
            if self._is_create_conflict(e):
                print("Deployment already exists")
            else:
                raise e
        try:
            resp = create_from_yaml(client.ApiClient(),
                                    path.join(path.dirname(__file__), "ops/manifests/db/db-deployment.yml"),
                                    namespace=self.namespace, verbose=True)
            print("Deployment created. status='%s'" % str(resp))
        except FailToCreateError as e:
            if self._is_create_conflict(e):
                print("Deployment already exists")
            else:
                raise e

        self._watch_db()

    @staticmethod
    def _is_create_conflict(e):
        if isinstance(e, ApiException):
            if e.status == 409:
                return True
        if isinstance(e, FailToCreateError):
            if e.api_exceptions is not None:
                ## lets quickly check if all status codes are 409 -> componetnes exist already
                if set(map(lambda x: x.status, e.api_exceptions)) == {409}:
                    return True
        return False

    def setup(self):
        """

        """
        # TODO: compile grid and task into image
        self.image_builder.deploy_image("experiments/optuna_minikube/dockerfile.trial", self.trial_tag, Path.root_path)
        print(f"Image: {self.trial_tag}")

    def run(self):
        """Start Trial Containers in Subprocesses
        """
        job_definition = {
            "worker_num": self.workerCount,
            "worker_cpu": self.workerCpu,
            "worker_mem": f"{self.workerMemory}Gi",
            "worker_image": self.trial_tag,
            "study_name": self.study_name,
            "metrics_ip": self.resources["metricsIP"],
        }

        with open(path.join(path.dirname(__file__), "ops/manifests/trial/job.yml"), "r") as f:
            job_template = Template(f.read())
            job_yml_objects = yaml.safe_load_all(job_template.substitute(job_definition))

        try:
            create_from_yaml(client.ApiClient(), yaml_objects=job_yml_objects, namespace=self.namespace, verbose=True)
        except FailToCreateError as e:
            if self._is_create_conflict(e):
                # lets remove the old one and try again
                client.BatchV1Api().delete_namespaced_job(name="optuna-trial", namespace=self.namespace)
                create_from_yaml(client.ApiClient(), yaml_objects=job_yml_objects, namespace=self.namespace,
                                 verbose=True)
            else:
                raise e

    def _getDBURL(self):
        postgres_sepc = client.CoreV1Api().read_namespaced_service(namespace=self.namespace, name="postgres")
        if postgres_sepc is not None:
            if len(postgres_sepc.spec.ports) > 0 and postgres_sepc.spec.ports[0].node_port > 0:
                # XXX: hardcoded credentaials - should match ops/mainifests/db/db-deployment.yaml#ostgres-config
                url = f"postgresql://postgresadmin:admin123@{self.master_ip}:{postgres_sepc.spec.ports[0].node_port}/postgresdb"
                print(url)
                return url
            raise Exception("Postgres DB not found - spec dose not have node port}" + str(postgres_sepc))
        raise Exception("Postgres DB URL not found")

    def collect_run_results(self):
        """Collect results form container or on master?
        """
        self._watch_trials()
        study = optuna.load_study(study_name=self.study_name, storage=self._getDBURL())
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
        if self.delete_after_run:
            client.CoreV1Api().delete_namespace(self.namespace)
            self.image_builder.cleanup(self.trial_tag)

    def _watch_db(self):
        w = watch.Watch()
        c = client.AppsV1Api()
        for e in w.stream(c.list_namespaced_deployment, namespace=self.namespace,
                          timeout_seconds=10,
                          field_selector="metadata.name=postgres"):
            deployment_spec = e["object"]
            if deployment_spec is not None:
                if deployment_spec.status.available_replicas is not None \
                        and deployment_spec.status.available_replicas > 0:
                    w.stop()
                    return True

        return False
