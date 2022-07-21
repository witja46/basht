

if __name__ == "__main__":
    from . import OptunaMinikubeBenchmark
    from ml_benchmark.benchmark_runner import BenchmarkRunner
    import subprocess
    from urllib.request import urlopen
    # The basic config for the workload. For testing purposes set epochs to one.
    # For benchmarking take the default value of 100
    # your ressources the optimization should run on
    resources = {
        "workerCpu": 2,
        "workerMemory": 2,
        "workerCount": 4,
        "metricsIP": urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip(),
        "kubernetesMasterIP": subprocess.check_output("minikube ip", shell=True).decode("utf-8").strip("\n"),
        "dockerImageTag": "tawalaya/optuna-trial:latest",
        "dockerImageBuilder": "minikube",
        "kubernetesNamespace": "optuna-study",
        "kubernetesContext": "minikube",
        "deleteAfterRun": True,
    } 

    #TODO: hyperparams.

    # import an use the runner
    runner = BenchmarkRunner(
        benchmark_cls=OptunaMinikubeBenchmark, resources=resources)
    runner.run()
