from experiments.optuna_minikube.optuna_benchmark import OptunaMinikubeBenchmark

if __name__ == "__main__":
    from ml_benchmark.benchmark_runner import BenchmarkRunner
    from urllib.request import urlopen
    # The basic config for the workload. For testing purposes set epochs to one.
    # For benchmarking take the default value of 100
    # your ressources the optimization should run on
    resource_definition = {
        "workerCpu": 2,
        "workerMemory": 2,
        "workerCount": 4,
        "metricsIP": urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip(),
        "studyName": "optuna-study",
        "dockerImageTag": "tawalaya/optuna-trial:latest",
        "dockerImageBuilder": "docker",
        "kubernetesNamespace": "optuna-study",
        "kubernetesContext": "admin@smile",
        "kubernetesMasterIP": "130.149.158.143",
        "deleteAfterRun": False,
    }

    #TODO: hyperparams.

    # import an use the runner
    runner = BenchmarkRunner(
        benchmark_cls=OptunaMinikubeBenchmark, resource_definition=resource_definition)
    runner.run()
