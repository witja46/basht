import logging
from os import path
from time import sleep
from experiments.katib_k8s.katib_benchmark import KatibBenchmark
from ml_benchmark.benchmark_runner import BenchmarkRunner
from urllib.request import urlopen

if __name__ == "__main__":
    metricsIP = urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip()
    logging.basicConfig(format='%(asctime)s Katib Benchmark %(levelname)s: %(message)s',level=logging.INFO)

    # read in base configuration

    resources={
        # "dockerUserLogin":"",
        # "dockerUserPassword":"",
        # "studyName":""
 
        "metricsIP": urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip(),
        "generateNewDockerImage": True,
        # "prometheus_url": "http://130.149.158.143:30041",
        "cleanUp": True ,
        "limitResources":False,
        "loggingLevel": logging.INFO,
      
        }

    repetions = 2
    for trials in [2,3,4,5]:
        
            sleep(3)
            logging.info(f"Starting Run with n_trails {trials}")
            try:
                resources["workerCount"] = trials
                resources["jobsCount"] = trials
                runner = BenchmarkRunner(benchmark_cls=KatibBenchmark, resources=resources)
                runner.run()
                sleep(7)
                runner = None
            except Exception as e:
                logging.warning(f'Failed Run  n_trails {trials} - {e}')
