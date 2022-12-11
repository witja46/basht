import logging
from os import path
from time import sleep
from experiments.katib_k8s.katib_benchmark import KatibBenchmark
from experiments.polyaxon_k8s.polyaxon_benchmark import PolyaxonBenchmark
from ml_benchmark.benchmark_runner import BenchmarkRunner
from urllib.request import urlopen

if __name__ == "__main__":
    metricsIP = urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip()
    logging.basicConfig(format='%(asctime)s Katib Benchmark %(levelname)s: %(message)s',level=logging.INFO)

    # read in base configuration
    experiments=[
           {   "experiment_titel":"clean_up",
            "variabel":"jobsCount",
            "values":[1],

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
            "undeploy":True,
            "deploy": False,

            "jobsCount":0
                       
        },

        {   "experiment_titel":"deploy",
            "variabel":"jobsCount",
            "values":[1],

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
            "deploy": True,

            "jobsCount":0
                       
        },

        # {   "experiment_titel":"tuning_scalability",
        #     "variabel":"jobsCount",
        #     "values":[1,2],

        #     "metricsIP": urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip(),
        #   #  "prometheus_url": "http://130.149.158.143:30041",
        #     "loggingLevel": logging.INFO,
        #     "imagePullPolicy": "IfNotPresent",
        #     "generateNewDockerImage": False,
        #  #  "dockerImageTag":"",
                   
        #     "limitResources":False,            
        #     "limitCpuTotal":"",
        #     "limitCpuWorker":"",
 
        #     "cleanUp": True ,
        #     "undeploy":False,
        #     "deploy": False,

        #     "jobsCount":0
                       
        # },
        {   "experiment_titel":"resources",
            "variabel":"limitCpuTotal",
            "values":["10"],

            "metricsIP": urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip(),
          #  "prometheus_url": "http://130.149.158.143:30041",
            "loggingLevel": logging.INFO,
            "imagePullPolicy": "IfNotPresent",
            "generateNewDockerImage": False,
         #  "dockerImageTag":"",
                   
            "limitResources":True,            
          
 
            "cleanUp": True ,
            "undeploy":False,
            "deploy": False,

            "jobsCount":1,
            "limitCpuTotal":"",
            "limitCpuWorker":"1000m",
                       
        },
        # {   
        #     "experiment_titel":"worker",
        #     "variabel":"limitCpuWorker",
        #     "values":["1000m","2000m"],

        #     "metricsIP": urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip(),
        #   #  "prometheus_url": "http://130.149.158.143:30041",
        #     "loggingLevel": logging.INFO,
        #     "imagePullPolicy": "IfNotPresent",
        #     "generateNewDockerImage": False,
        #  #  "dockerImageTag":"",
                   
        #     "limitResources":True,            
          
 
        #     "cleanUp": True ,
        #     "undeploy":False,
        #     "deploy": False,

        #     "jobsCount":2,
        #     "limitCpuTotal":20,
        #     "limitCpuWorker":"",
                       
        # }
        
        
        
        
        ]
    
    

    reps = 2
    for rep in range(1,reps+1):
        for exp in experiments:

            for var in exp["values"]:
                resources = None
              
                logging.info(f'Katib Starting rep {rep} of  {exp["experiment_titel"]} with {exp["variabel"]} of {var}  ')
                try:
                    resources = exp.copy()
                    resources[exp["variabel"]] = var
                    resources["studyName"] = f'study-rep-{rep}-{exp["variabel"]}-{var}-katib'.lower()
                    resources["repetition"] = rep
                 
                
                    runner = BenchmarkRunner(benchmark_cls=KatibBenchmark, resources=resources)
                    runner.run()
                   
                    sleep(10)
                    runner = None
                except Exception as e:
                    logging.warning(f'Failed Run  rep {rep} of  {exp["experiment_titel"]} with {exp["variabel"]} of {var}  ')


                logging.info(f'Polyaxon Starting rep {rep} of  {exp["experiment_titel"]} with {exp["variabel"]} of {var}  ')
                try:
                    resources = None
                    resources = exp.copy()
                    resources[exp["variabel"]] = var
                    resources["studyName"] = f'{exp["experiment_titel"]}-rep-{rep}-{exp["variabel"]}-{var}-polyaxon'.lower()
                    resources["repetition"] = rep
                 
                
                    runner = BenchmarkRunner(benchmark_cls=PolyaxonBenchmark, resources=resources)
                    runner.run()
                   
                    sleep(10)
                    runner = None
                    
                except Exception as e:
                    logging.warning(f'Failed Run  rep {rep} of  {exp["experiment_titel"]} with {exp["variabel"]} of {var}  ')
