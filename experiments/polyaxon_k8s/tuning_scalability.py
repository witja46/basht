import logging
from os import path
from time import sleep
from experiments.polyaxon_k8s.polyaxon_benchmark import PolyaxonBenchmark
from ml_benchmark.benchmark_runner import BenchmarkRunner
from urllib.request import urlopen

if __name__ == "__main__":
    metricsIP = urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip()
    logging.basicConfig(format='%(asctime)s Polyaxon Benchmark %(levelname)s: %(message)s',level=logging.INFO)

    # read in base configuration

    resources={
        # "dockerUserLogin":"",
        # "dockerUserPassword":"",
        # "studyName":""
 
        "metricsIP": urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip(),
        "generateNewDockerImage": False,
        # "prometheus_url": "http://130.149.158.143:30041",
        "cleanUp": True ,
        "limitResources":False,
        "loggingLevel": logging.INFO,
      
        }

    repetions = 2
    for trials in [1,2,3,4]:
            for imagePullPolicy in ["IfNotPresent"]:
            
                logging.info(f"Starting Run with n_trails {trials}, and ImagePullPolicy {imagePullPolicy}")
                try:
                    resources["workerCount"] = trials
                    resources["jobsCount"] = trials
                    resources["imagePullPolicy"] = imagePullPolicy
                    runner = BenchmarkRunner(benchmark_cls=PolyaxonBenchmark, resources=resources)
                    runner.run()
                    resources["generateNewDockerImage"] = False
                    sleep(7)
                    runner = None
                except Exception as e:
                    logging.warning(f'Failed Run  n_trails {trials} - {e}')