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
       #  "prometheus_url": "http://130.149.158.143:30041",
        "cleanUp": True ,
        "limitResources":True,
        "loggingLevel": logging.INFO,

        }

    repetions = 2
    rep = 1

    for trials in [5]:
        for cores_pro_worker in ["300m","500m","600m","800m", "1000m",  "1200m",  "1400m", "1800m" , "2000m","2400m","2800m"]:

            cores_total = 60
            sleep(3)
            logging.info(f"Cpu Worker limit {cores_pro_worker} Total limit of cores {cores_total} Starting Run with n_trails {trials} ")
            try:
                resources["studyName"] = f'study-worker-{cores_pro_worker}-total-{cores_total}-rep-{rep}-trials-{trials}'
                resources["undeploy"] = False
                resources["deploy"]=False
                resources["type"] = "worker_scalability"
                resources["workerCount"] = trials
                resources["jobsCount"] = trials
                resources["limitCpuTotal"] = cores_total
                resources["limitCpuWorker"] = cores_pro_worker
                runner = BenchmarkRunner(benchmark_cls=KatibBenchmark, resources=resources)
                runner.run()
                resources["generateNewDockerImage"] = False
                sleep(7)
                runner = None
            except Exception as e:
                logging.warning(f'Failed Run  n_trails {trials}  {cores_pro_worker}- {e}')                                                                                         
