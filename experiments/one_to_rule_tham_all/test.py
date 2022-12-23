import logging
from os import path
import os
from statistics import mean
from time import sleep
from experiments.katib_k8s.katib_benchmark import KatibBenchmark
from experiments.polyaxon_k8s.polyaxon_benchmark import PolyaxonBenchmark
from ml_benchmark.benchmark_runner import BenchmarkRunner
from urllib.request import urlopen

import json 

def load_data(folder_name,json_id,exp_title,repetition):
    folder = os.listdir(f"./{folder_name}")
    folder.sort()
    data = []
    for file in folder:
        with open(f"{folder_name}/{file}","r") as f:
            exp = json.load(f)
            if(exp["benchmark_configuration"]["resources"].get("id","") == json_id and exp["benchmark_configuration"]["resources"]["experiment_titel"]== exp_title and exp["benchmark_configuration"]["resources"]["repetition"] == repetition):
                data.append(exp)
    return data

def corretct_data(to_corect,corect_values,exp_id,folder_name):
  
    return data



if __name__ == "__main__":
    print("jeb")
    id = 57482 
    

    print("id== ",id)
    # for x in range(1,3):
    #     print("x=",x)
    #     data =    load_data("../katib_k8s/benchmark__KatibBenchmark",id,"resources",x)
    #     print(len(data))
    #     for exp in data:
    #       res = exp["benchmark_configuration"]["resources"]
    #       print(res["limitCpuWorker"],res["limitCpuTotal"])    
   
    folder_name = "../katib_k8s/benchmark__KatibBenchmark"
    folder_name = "../polyaxon_k8s/benchmark__PolyaxonBenchmark"

    # folder = os.listdir(f"./{folder_name}")
    # folder.sort()
    # data = []
    # for file in folder:
    #     with open(f"{folder_name}/{file}","r") as f:
    #         exp = json.load(f)
    #         exp_res= exp["benchmark_configuration"]["resources"]
            
          
    #         if(exp_res.get("experiment_titel","")== "deploy"):
    #           for lat in exp["benchmark_metrics"]["latency"]:
    #             if(lat["function_name"]=="deploy"):

    #               if(lat["duration_sec"] > 40):
    #                 data.append(lat["duration_sec"])
    #                 print(lat["duration_sec"])
    # print("mean time = ", mean(data))
          



    id = 5999692251
    print("guwno")
    limitCpuWorker  ="1000m"
    folder = os.listdir(f"./{folder_name}")
    folder.sort()
    data = []
    for file in folder:
        with open(f"{folder_name}/{file}","r") as f:
            exp = json.load(f)
            exp_res= exp["benchmark_configuration"]["resources"]
            
            if(exp_res.get("id","") == id and exp_res["repetition"]== 4):
                data.append(exp)
                print(exp_res["limitCpuWorker"],exp_res["limitCpuTotal"],exp_res["repetition"],exp_res["values"],file,)
                exp["benchmark_configuration"]["resources"]["repetition"] = 3
                # with open(f"{folder_name}/{file}", "w") as outfile:
                #       json.dump(exp, outfile)