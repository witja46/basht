from argparse import ArgumentParser
import json
import logging
import random
from os import path
from time import sleep
from experiments.katib_k8s.katib_benchmark import KatibBenchmark
from experiments.polyaxon_k8s.polyaxon_benchmark import PolyaxonBenchmark
from ml_benchmark.benchmark_runner import BenchmarkRunner
from urllib.request import urlopen



def run_experiment(rep,exp,var,runs_id,pause_between,framework_name):
    resources = None

    logging.info(f"Waiting {pause_between} sec before starting {exp['latexTitle']} on {framework_name}")
    sleep(pause_between)

    logging.info(f'{framework_name} Starting rep {rep} of  {exp["latexTitle"]} with {exp["variabel"]} of {var}  ')
    try:
        resources = exp.copy()
        resources[exp["variabel"]] = var
        resources["id"] = runs_id
        resources["studyName"] = f'{exp["experiment_titel"]}-rep-{rep}-{exp["variabel"]}-{var}-{framework_name}-{runs_id}'.lower()
        resources["repetition"] = rep
        
        if(framework_name == "Katib"):
            runner = BenchmarkRunner(benchmark_cls=KatibBenchmark, resources=resources)
            runner.run()
        elif(framework_name == "Polyaxon"):
            runner = BenchmarkRunner(benchmark_cls=PolyaxonBenchmark, resources=resources)
            runner.run()
        else:
            raise Exception(f'{framework_name} must be equel to eather "Katib" or "Polyaxon" ')
        runner = None
        logging.info(f"Waiting  {pause_between} sec before starting {exp['latexTitle']}")
        sleep(pause_between)
    except Exception as e:
        logging.warning(f'Failed Run  rep {rep} of  {exp["experiment_titel"]} with {exp["variabel"]} of {var}  ')








if __name__ == "__main__":
    metricsIP = urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip()
    logging.basicConfig(format='%(asctime)s Katib Benchmark %(levelname)s: %(message)s',level=logging.INFO)

    # read in base configuration
    clean_and_deploy=[
          {   "experiment_titel":"clean_up",
            "variabel":"jobsCount",
            "values":[1],

            "metricsIP": urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip(),
            # "prometheus_url": "http://130.149.158.143:30041",
            "loggingLevel": logging.INFO,
            "imagePullPolicy": "IfNotPresent",
            "generateNewDockerImage": False,
         #  "dockerImageTag":"",

            "limitResources":False,
            "limitCpuTotal":"",
            "limitCpuWorker":"",

            "cleanUp": True ,
            "undeploy":True,
            "deploy": True,

            "jobsCount":1,
            "limitCpuTotal":"",
            "limitCpuWorker":"",
             "generatePlots": False,
      "latexTitle": "Clean up operation ",
      "latexDescritption": "Clean up execution "
   

        },

        {   "experiment_titel":"deploy",
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
            "deploy": True,

            "jobsCount":1,
            "limitCpuTotal":"",
            "limitCpuWorker":"4000m",
            "generatePlots": True,
            "latexTitle": "Deploy operation",
            "latexDescritption": "Deploy executed on the begining and in between the experiments"
   

        }
    ]


      
        
        
        
     
    parser = ArgumentParser()
    parser.add_argument("-f", "--file", dest="json_path",
                        help="specify the experiments description json", metavar="FILE")
    args = parser.parse_args()
    
    json_path =  args.json_path
    with open(f"{json_path}","r") as f:
         exp_json =  json.load(f)


    experiments = exp_json["experiments"]
    if(exp_json["clean_and_deploy"]):
        experiments =  clean_and_deploy + experiments 
    print(experiments)
    
    
    repetitions = exp_json["repetitions"]

    runs_id = exp_json["json_id"]
    run_on_framworks = exp_json["run_on_framworks"]
    pause_between= exp_json.get("pause_between",0)

    limitation = ""
    

    for rep in range(1,repetitions+1):
            # katib_bench = KatibBenchmark(resources={})
            # polyaxon_bench = PolyaxonBenchmark(resources={})
            # katib_bench.undeploy()
            # polyaxon_bench.undeploy()



            for exp in experiments:
                
                
                
                for var in exp["values"]:
                    for framework_name in run_on_framworks:
                        run_experiment(rep,exp,var,runs_id,pause_between,framework_name)
                    
                    
                    
                    
                    # resources = None

                    # logging.info(f"Waiting 10 sec before starting {exp['latexTitle']}")
                    # sleep(10)

                    # logging.info(f'Katib Starting rep {rep} of  {exp["latexTitle"]} with {exp["variabel"]} of {var}  ')
                    # try:
                    #     resources = exp.copy()
                    #     resources[exp["variabel"]] = var
                    #     resources["id"] = runs_id
                    #     resources["studyName"] = f'{exp["experiment_titel"]}-rep-{rep}-{exp["variabel"]}-{var}-katib-{runs_id}'.lower()
                    #     resources["repetition"] = rep

                    #     runner = BenchmarkRunner(benchmark_cls=KatibBenchmark, resources=resources)
                    #     runner.run()

                    #     runner = None
                    # except Exception as e:
                    #     logging.warning(f'Failed Run  rep {rep} of  {exp["experiment_titel"]} with {exp["variabel"]} of {var}  ')

                    # logging.info(f"Waiting 10 sec before starting {exp['latexTitle']} on polyaxon")
                    # sleep(10)
                    # logging.info(f'Polyaxon Starting rep {rep} of  {exp["latexTitle"]} with {exp["variabel"]} of {var}  ')
                    # try:
                    #     resources = None
                    #     resources = exp.copy()
                    #     resources["id"] = runs_id
                    #     resources[exp["variabel"]] = var
                    #     resources["studyName"] = f'{exp["experiment_titel"]}-rep-{rep}-{exp["variabel"]}-{var}-polyaxon-{runs_id}'.lower()
                    #     resources["repetition"] = rep


                    #     runner = BenchmarkRunner(benchmark_cls=PolyaxonBenchmark, resources=resources)
                    #     runner.run()


                    #     runner = None

                    # except Exception as e:
                    #     logging.warning(f'Failed Run  rep {rep} of  {exp["experiment_titel"]} with {exp["variabel"]} of {var}  ')














  # {   "experiment_titel":"resources",
        #     "variabel":"limitCpuTotal",
            
        #  "values":[4,5,6,7,8,9,10,12,14,16,18,20,22,25,30],
        #     "values":[20,30],
        #     "metricsIP": urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip(),
        #     "prometheus_url": "http://130.149.158.143:30041",
        #     "loggingLevel": logging.INFO,
        #     "imagePullPolicy": "IfNotPresent",
        #     "generateNewDockerImage": False,
        #  #  "dockerImageTag":"",
                   
        #     "limitResources":True,            
          
 
        #     "cleanUp": True ,
        #     "undeploy":False,
        #     "deploy": False,

        #     "jobsCount":10,
        #     "limitCpuTotal":"",
        #     "limitCpuWorker":"1000m",
                       
        # },














        # {   "experiment_titel":"clean_up",
        #     "variabel":"jobsCount",
        #     "values":[1],

        #     "metricsIP": urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip(),
        #     "prometheus_url": "http://130.149.158.143:30041",
        #     "loggingLevel": logging.INFO,
        #     "imagePullPolicy": "IfNotPresent",
        #     "generateNewDockerImage": False,
        #  #  "dockerImageTag":"",

        #     "limitResources":False,
        #     "limitCpuTotal":"",
        #     "limitCpuWorker":"",

        #     "cleanUp": True ,
        #     "undeploy":True,
        #     "deploy": True,

        #     "jobsCount":1,
        #     "limitCpuTotal":"",
        #     "limitCpuWorker":"",

        # },

        # {   "experiment_titel":"deploy",
        #     "variabel":"limitCpuTotal",
        #     "values":["10"],

        #     "metricsIP": urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip(),
        #      "prometheus_url": "http://130.149.158.143:30041",
        #     "loggingLevel": logging.INFO,
        #     "imagePullPolicy": "IfNotPresent",
        #     "generateNewDockerImage": False,
        #  #  "dockerImageTag":"",

        #     "limitResources":True,


        #     "cleanUp": True ,
        #     "undeploy":False,
        #     "deploy": True,

        #     "jobsCount":1,
        #     "limitCpuTotal":"",
        #     "limitCpuWorker":"4000m",

        # },
        
        # {"experiment_titel":"resources",
        # "variabel":"limitCpuTotal",
        # "values":[4,5,6,7,8,9,10,12,14,16,18,20,22,25,30],

        # "metricsIP": urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip(),
        # "prometheus_url": "http://130.149.158.143:30041",
        # "loggingLevel": logging.INFO,
        # "imagePullPolicy": "IfNotPresent",
        # "generateNewDockerImage": False,
        # #  "dockerImageTag":"",
                
        # "limitResources":True,            
        

        # "cleanUp": True ,
        # "undeploy":False,
        # "deploy": False,

        # "jobsCount":10,
        # "limitCpuTotal":"",
        # "limitCpuWorker":"2000m",
                    
        # },















        # {   "experiment_titel":"clean_up",
        #     "variabel":"jobsCount",
        #     "values":[1],

        #     "metricsIP": urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip(),
        #     "prometheus_url": "http://130.149.158.143:30041",
        #     "loggingLevel": logging.INFO,
        #     "imagePullPolicy": "IfNotPresent",
        #     "generateNewDockerImage": False,
        #  #  "dockerImageTag":"",

        #     "limitResources":False,
        #     "limitCpuTotal":"",
        #     "limitCpuWorker":"",

        #     "cleanUp": True ,
        #     "undeploy":True,
        #     "deploy": True,

        #     "jobsCount":1,
        #     "limitCpuTotal":"",
        #     "limitCpuWorker":"",

        # },

        # {   "experiment_titel":"deploy",
        #     "variabel":"limitCpuTotal",
        #     "values":["10"],

        #     "metricsIP": urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip(),
        #      "prometheus_url": "http://130.149.158.143:30041",
        #     "loggingLevel": logging.INFO,
        #     "imagePullPolicy": "IfNotPresent",
        #     "generateNewDockerImage": False,
        #  #  "dockerImageTag":"",

        #     "limitResources":True,


        #     "cleanUp": True ,
        #     "undeploy":False,
        #     "deploy": True,

        #     "jobsCount":1,
        #     "limitCpuTotal":"",
        #     "limitCpuWorker":"4000m",

        # },
        
        # {"experiment_titel":"resources",
        # "variabel":"limitCpuTotal",
        # "values":[4,5,6,7,8,9,10,12,14,16,18,20,22,25,30],

        # "metricsIP": urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip(),
        #   "prometheus_url": "http://130.149.158.143:30041",
        # "loggingLevel": logging.INFO,
        # "imagePullPolicy": "IfNotPresent",
        # "generateNewDockerImage": False,
        # #  "dockerImageTag":"",
                
        # "limitResources":True,            
        

        # "cleanUp": True ,
        # "undeploy":False,
        # "deploy": False,

        # "jobsCount":10,
        # "limitCpuTotal":"",
        # "limitCpuWorker":"500m",
                    
        # },
        
        # {"experiment_titel":"resources",
        # "variabel":"limitCpuTotal",
        # "values":[20,30],

        # "metricsIP": urlopen("https://checkip.amazonaws.com").read().decode("utf-8").strip(),
        # #  "prometheus_url": "http://130.149.158.143:30041",
        # "loggingLevel": logging.INFO,
        # "imagePullPolicy": "IfNotPresent",
        # "generateNewDockerImage": False,
        # #  "dockerImageTag":"",
                
        # "limitResources":True,            
        

        # "cleanUp": True ,
        # "undeploy":False,
        # "deploy": False,

        # "jobsCount":1,
        # "limitCpuTotal":"",
        # "limitCpuWorker":"500m",
                    
        # },
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
                       
        # 