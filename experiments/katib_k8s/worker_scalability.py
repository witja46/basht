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
        "generateNewDockerImage": False,
        #"prometheus_url": "http://130.149.158.143:30041",
        "cleanUp": True ,
        "limitResources":True,
        "loggingLevel": logging.INFO,
      
        }

    repetions = 2
  
        




    for cores_total in [12,24]:
        for trials in [2,4]:
            for cores_pro_worker in range(2,20,2):
                sleep(3)
                logging.info(f"Cpu Worker limit {cores_pro_worker}00m Total limit of cores {cores_total} Starting Run with n_trails {trials} ")
                try:
                    resources["workerCount"] = trials
                    resources["jobsCount"] = trials
                    resources["limitCpuTotal"] = cores_total
                    resources["limitCpuWorker"] = f"{cores_pro_worker}00m" #range from 200m to 2000m
                    runner = BenchmarkRunner(benchmark_cls=KatibBenchmark, resources=resources)
                    runner.run()
                    resources["generateNewDockerImage"] = False
                    sleep(7)
                    runner = None
                except Exception as e:
                    logging.warning(f'Failed Run  n_trails {trials} {cores_total} {cores_pro_worker}- {e}')
