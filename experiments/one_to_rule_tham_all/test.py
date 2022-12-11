import logging
from os import path
from time import sleep
from experiments.katib_k8s.katib_benchmark import KatibBenchmark
from experiments.polyaxon_k8s.polyaxon_benchmark import PolyaxonBenchmark
from ml_benchmark.benchmark_runner import BenchmarkRunner
from urllib.request import urlopen

if __name__ == "__main__":
    print("jASDeb".lower())
    exp =  {   "experiment_titel":"tuning_scalability",
            "variabel":"jobsCount",
            "values":[1,2],

            "metricsIP": urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip(),
          #  "prometheus_url": "http://130.149.158.143:30041",
            "loggingLevel": logging.INFO,
            "imagePullPolicy": "IfNotPresent",
            "generateNewDockerImage": False,
         #  "dockerImageTag":"",
                   
            "limitResources":False,            
            "limitCpuTotal":"",
            "limitCpuWorker":"",
 
            "cleanUp": True ,
            "undeploy":False,
            "deploy": False,

            "jobsCount":0
                       
        }
    print(exp["variabel"])
    print(exp["variabel"].lower())
    
