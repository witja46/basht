
from asyncio import subprocess
from concurrent.futures import process
from itertools import count
import json
from os import path 
import os
from socket import timeout
import sys
from time import sleep
import random
from kubernetes import client, config,watch
from kubernetes.client.rest import ApiException
from string import Template
import docker
from ml_benchmark.benchmark_runner import Benchmark
import requests
import subprocess
import psutil
import logging as log



class PolyaxonBenchmark(Benchmark):

    def __init__(self, resources) -> None:
        # self.objective = objective
        # self.grid = grid
        self.resources = resources
        self.group="kubeflow.org"
        self.version="v1beta1"
        self.namespace='polyaxon'
        self.plural="experiments"
        self.experiment_file_name = "grid.yaml"
        self.project_description = "Somer random description"
        self.polyaxon_addr="http://localhost:31833/"
        self.post_forward_process=False
        
        config.load_kube_config()

        self.logging_level= self.resources.get("loggingLevel",log.CRITICAL)

        log.basicConfig(format='%(asctime)s Polyaxon Benchmark %(levelname)s: %(message)s',level=self.logging_level)

    
        if "dockerImageTag" in self.resources:
            self.trial_tag = self.resources["dockerImageTag"]
        else:
            self.trial_tag = "mnist_polyaxon:latest"

        if "dockerUserLogin" in self.resources:
            self.docker_user = self.resources["dockerUserLogin"]
            self.trial_tag =  f'{self.docker_user}/{self.trial_tag}'
        else:
            self.docker_user = ""
            self.trial_tag = "witja46/mnist_polyaxon:latest"
        
        if "dockerUserPassword" in self.resources:
            self.docker_pasword = self.resources["dockerUserPassword"]
        else:
            self.docker_pasword = ""        


        if "studyName" in self.resources:
            self.study_name = self.resources["studyName"]
        else:
            self.study_name = f"polyaxon-study-{random.randint(0, 100)}"

        if "workerCpu" in self.resources:
            self.workerCpu = self.resources["workerCpu"]
        else:
            self.workerCpu = 2

        if "workerMemory" in resources:
            self.workerMemory = self.resources["workerMemory"]
        else:
            self.workerMemory = 2

        if "workerCount" in resources:
            self.workerCount = self.resources["workerCount"]
        else:
            self.workerCount = 5

        if "jobsCount" in resources:
            self.jobsCount = self.resources["jobsCount"]
        else:
            self.jobsCount = 6
        
    def deploy(self):
        """
            With the completion of this step the desired architecture of the HPO Framework should be running
            on a platform, e.g,. in the case of Kubernetes it referes to the steps nassary to deploy all pods
            and services in kubernetes.
        """
        
        log.info("Adding polyaxon to helm repo:")
        res = os.popen('helm repo add polyaxon https://charts.polyaxon.com').read()
        log.info(res)

        #TODO deploy via helm for better error handling and easier configuration?
        log.info("Deploying polyaxon to minikube:")
        res = os.popen('polyaxon admin deploy -t minikube').read()
        log.info(res)

      
      
        

        config.load_kube_config()
        w = watch.Watch()
        c = client.CoreV1Api()
        # c = client.AppsV1Api()
        deployed = 0


        log.info("Waiting for polyaxon pods to be read:")
        # From all pods that polyaxon starts we are onlly really intrested for following 4 that are crucial for runnig of the experiments 
        monitored_pods = ["polyaxon-polyaxon-streams","polyaxon-polyaxon-operator","polyaxon-polyaxon-gateway","polyaxon-polyaxon-api"]
        # TODO changing to list_namespaced_deployments?
        for e in w.stream(c.list_namespaced_pod, namespace="polyaxon"):
            ob = e["object"]          
            
            for name in monitored_pods:

                #checking if it is one of the pods that we want to monitor 
                if name in ob.metadata.name:
                    
                    # Checking if the pod already is runnig and its underlying containers are ready
                    if ob.status.phase == "Running" and ob.status.container_statuses[0].ready: 
                        log.info(f'{ob.metadata.name} is ready')
                        monitored_pods.remove(name)
                        deployed = deployed + 1

                        #if all monitored pods are running the deployment process was ended
                        if(deployed == 4 ):
                            w.stop()
                            log.info("Finished deploying crucial pods")
                            

        
  

        # Starting post forwarding to the polyaxon api in the background
        log.info("Starting post-forward to polyaxon api:")
        self.post_forward_process = subprocess.Popen("kubectl port-forward  svc/polyaxon-polyaxon-api 31833:80  -n polyaxon",shell=True,stdout=subprocess.PIPE)




      
        
    def setup(self):
        """
        Every Operation that is needed before the actual optimization (trial) starts and that is not relevant
        for starting up workers or the necessary architecture.
        """
       
        #creating experiment yaml          
             
        experiment_definition = {
            "worker_num": self.workerCount,
            "jobs_num":self.jobsCount,
            "worker_cpu": self.workerCpu,
            "worker_mem": f"{self.workerMemory}Gi",
            "worker_image": self.trial_tag,
            "study_name": self.study_name,
            "trialParameters":"${trialParameters.learningRate}"
        }

        #loading and filling the template
        with open(path.join(path.dirname(__file__), "experiment_template.yaml"), "r") as f:
            job_template = Template(f.read())
            job_yml_objects = job_template.substitute(experiment_definition)
            
        #writing the experiment definition into the file        
        with open(path.join(path.dirname(__file__), self.experiment_file_name), "w") as f:
            f.write(job_yml_objects)
        log.info("Experiment yaml created")
      
      
        # Creating new docker image if credentials were passed
        if "dockerUserLogin" in self.resources:
           
            #creating task docker image  
            log.info("Creating task docker image")  
            self.client = docker.client.from_env()
            image, logs = self.client.images.build(path="./mnist_task",tag=self.trial_tag)
            log.info(f"Image: {self.trial_tag}")
            for line in logs  :
                log.info(line) 
            

            #TODO check if the image is runing properly and there is no  problems with it

            #pushing to repo
            self.client.login(username=self.docker_user, password=self.docker_pasword)
            for line in self.client.images.push(self.trial_tag, stream=True, decode=True):
                log.info(line) 
            
        

    def run(self):

        #TODO add error handling 
        log.info("Creating new project:")
        project = requests.post(f'{self.polyaxon_addr}/api/v1/default/projects/create', json={"name": self.study_name, "description": self.project_description})
        log.info(project.text)


        #TODO find out where to pass the --eager flag so that the run can be created with help of api
        # with open(path.join(path.dirname(__file__), self.experiment_file_name), "r") as f:
        #     body = f.read()
        #     log.info(body)
        #     run = requests.post(f'{self.polyaxon_addr}/api/v1/default/{self.study_name}/runs',json={"content":body,"eager":True ,"tags":["--eager"],"meta_info":{"eager":True,"--eager":True,"flags":"--eager"}})
        #     log.info(run.text)
      
      
        log.info("Starting polyaxon experiment:")
        res = os.popen(f'polyaxon run -f ./{self.experiment_file_name} --project {self.study_name} --eager').read()
        log.info(res)

        
        #TODO check if there is no problem with the image
        
        #TODO switch to kubernetes api for monitoring runing trials  
        log.info("Waiting for the run to finish:")
        finished = False
        while not finished:
            runs = self.get_succeeded_runs()
            log.info(f'{runs["count"]} jobs out of {self.jobsCount} succeded')
            
            #checking if all runs were finished
            finished = runs["count"] == self.jobsCount
            sleep(1)
        return 


    def collect_benchmark_metrics(self):
        pass



    def get_succeeded_runs(self, sort_by="duration"):
        
        #TODO add error handling acording to polyaxon api 
        res = requests.get(f'{self.polyaxon_addr}/api/v1/default/{self.study_name}/runs?query=status:succeeded&sort={sort_by}') 
        result = json.loads(res.text)
        return result

    def collect_run_results(self):
        

        log.info("Collecting run results:")
        result = self.get_succeeded_runs()
        log.info(json.dumps(result,indent=4))               
               
        # log.info("\n Experiment finished with following optimal trial:")
        # log.info(result["results"][0])
        return result["results"]
    
    def test(self):
        return super().test()

    def undeploy(self):
        
        if(self.post_forward_process):
            log.info("Terminating post  forwarding process:")
            process = psutil.Process(self.post_forward_process.pid)
            for proc in process.children(recursive=True):
                proc.kill()
            process.kill()
      


        #TODO changing to undeploying with helm?
        log.info("Undeploying polyaxon:")
        p = subprocess.Popen(["polyaxon", "admin" ,"teardown"],shell=True,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        out,err = p.communicate(input=b"y") 
        p.terminate()
             
    


        # Waiting untill all polyaxon pods get terminated 
        config.load_kube_config()
        w = watch.Watch()
        c = client.CoreV1Api()
        deployed = 0
        log.info("Waiting for polyaxon pods to be terminated:")
        for e in w.stream(c.list_namespaced_pod, namespace=self.namespace):
            ob = e["object"]
               
            log.debug(f'{deployed} pods out of 4 were killed')
            log.debug("\n new in stream:\n")
            log.debug(ob.metadata.name,ob.status.phase)

            if not ob.status.container_statuses[0].ready:
                log.info(f'Containers of {ob.metadata.name} are terminated')
                deployed = deployed + 1
                if(deployed == 4 ):
                    w.stop()
                    # log.info("Finished ")
                    break
        
      
        log.info("Killed all pods deleteing the namespace:")
        res = c.delete_namespace_with_http_info(name=self.namespace)
        

        #TODO somehow handel the timouts?
        log.info("Checking status of the deleted namespace:")  
        for e in w.stream(c.list_namespace):
            ob = e["object"]
            # if the status of our namespace was changed we check if it the namespace was really removed from the cluster by requesting and expecting it to be not found
            #TODO do this in other way

            
            if ob.metadata.name == self.namespace:
                try:
                    log.debug(c.read_namespace_status_with_http_info(name=self.namespace))
                except ApiException as err:
                    log.info(err)
                    log.info("Namespace sucessfully deleted")
                    w.stop()
                    break

        log.info("Finished undeploying")


if __name__ == "__main__":
    #main()
    # bench = PolyaxonBenchmark(resources={
    #         "dockerUserLogin":"",
    #         "dockerUserPassword":"",
    #     # "studyName":""
    #     "jobsCount":5,
    #     "workerCount":5,
    #     "loggingLevel":log.INFO
    #     })
    # bench.deploy() 
    # bench.setup()
    # bench.run()
    # bench.collect_run_results()
    # bench.undeploy()

    resources={
        #    "dockerUserLogin":"",
        #    "dockerUserPassword":"",
        # "studyName":""
        "jobsCount":5,
        "workerCount":5,
        "loggingLevel":log.INFO
    }
    from ml_benchmark.benchmark_runner import BenchmarkRunner
    runner = BenchmarkRunner(
        benchmark_cls=PolyaxonBenchmark, resources=resources)
    runner.run()

