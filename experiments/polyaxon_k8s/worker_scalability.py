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
         #"prometheus_url": "http://130.149.158.143:30041",
        "cleanUp": True ,
        "limitResources":True,
        "loggingLevel": logging.INFO,
      
        }

    repetions = 2
    rep = 1
    for cores_pro_worker in ["300","500m","600m","800m", "1000m",  "1200m",  "1400m", "1800m" , "2000m","2400m","2800m"]:
        for trials in [5,10]:

            cores_total = 60
            sleep(3)
            logging.info(f"Cpu Worker limit {cores_pro_worker} Total limit of cores {cores_total} Starting Run with n_trails {trials} ")
            try:
                resources["studyName"] = f'study-worker-{cores_pro_worker}-total-{cores_total}-rep-{rep}-trials-{trials}'
                resources["undeploy"] = False
                resources["deploy"]= False
                
                resources["workerCount"] = trials
                resources["jobsCount"] = trials
                resources["limitCpuTotal"] = cores_total       
                resources["limitCpuWorker"] = cores_pro_worker
                runner = BenchmarkRunner(benchmark_cls=PolyaxonBenchmark, resources=resources)
                runner.run()
                resources["generateNewDockerImage"] = False
                sleep(7)
                runner = None
            except Exception as e:
                logging.warning(f'Failed Run  n_trails {trials}  {cores_pro_worker}- {e}')
