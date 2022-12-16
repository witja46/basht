from matplotlib import pyplot as plt
import json
from datetime import datetime,timedelta
import os
import logging as log

from statistics import mean

logging_level= log.INFO
log.basicConfig(level=logging_level)



def load_data(folder_name,json_id,exp_title,repetition):
    folder = os.listdir(f"./{folder_name}")
    folder.sort()
    data = []
    for file in folder:
        with open(f"{folder_name}/{file}","r") as f:
            exp = json.load(f)
            exp_res= exp["benchmark_configuration"]["resources"]
            if(exp_res.get("id","") == json_id and exp_res.get("experiment_titel","")== exp_title and exp["benchmark_configuration"]["resources"]["repetition"] == repetition):
                data.append(exp)
    return data






def toTime(time_string):
    format =  "%Y-%m-%d %H:%M:%S.%f"
    return datetime.strptime(time_string,format)



phases = ["deploy","setup","run","collect_run_results","test","collect_benchmark_metrics"]

#takes array of experiments jsons and converts it to sorted dict stup[i] gives the setup time of i-th experiment 
def sort_experiments(data,sort_by="jobsCount"):

    
    if(sort_by== "limitCpuWorker"):
        for exp in data:
            exp["benchmark_configuration"]["resources"][sort_by] = int(exp["benchmark_configuration"]["resources"][sort_by][:-1])

   
    data.sort(key=lambda x :x["benchmark_configuration"]["resources"][sort_by])



    sorted = {
        f"{sort_by}":[],
        "deploy" : [],
        "setup"  : [],
        "run"  : [],
        "collect_run_results":[],
        "test":[],
        "collect_benchmark_metrics":[],
        "validate"  : [],
        "train":[],
        "trials":[],
        "resources":[]
        }


    for exp in data:
        sorted[sort_by].append(exp["benchmark_configuration"]["resources"][sort_by]) 
        sorted["trials"].append(exp["benchmark_configuration"]["resources"][sort_by])

        sorted["resources"].append(exp["benchmark_configuration"]["resources"])
        latencys = exp["benchmark_metrics"]["latency"]
        train = []
        validate = []
      
        for latency in latencys:
            if latency["function_name"]=="train":
                train.append(latency)
            elif latency["function_name"]=="validate":
                validate.append(latency)
            else:
                #adding one houer xddddd
                corrected_start_time = toTime(latency["start_time"]) - timedelta(hours=1)
                corrected_end_time = toTime(latency["end_time"]) - timedelta(hours=1)
                latency["start_time"] = corrected_start_time
                latency["end_time"]= corrected_end_time
                sorted[latency["function_name"]].append(latency)
        
        sorted["train"].append(train)
        sorted["validate"].append(validate)

    return sorted



        
        

def get_phases_durations(sorted_experiment):
    phases = ["deploy","setup","run","collect_run_results","test","collect_benchmark_metrics"]
    values={}
    for phase in phases:
        values[phase]=[]
        for latency in sorted_experiment[phase]:
            values[phase].append(latency["duration_sec"])
    return values
    








#print(data)

# plt.plot(x, values["run"])
# plt.show()

#havin fun with the train times 

# calculates the avergate trial time in the experiment 
# input train_times_array of one experiment and it number 
def avg_trial_time(train_times_array,exp_num):
    count = 0.0
    sum = 0.0
    for train in train_times_array:
        sum= sum + (train["end_time"] - train["start_time"]).total_seconds()
        count+=1
    # if(count != sorted["trials"][exp_num]):
    #     print(f'{exp_num} count {count} != {sorted["trials"][exp_num]} fuck')
    #     return "fuck"

    return sum / count
 

#average trial tuning phase time
# avg_exp_train = []
# for i,exp in enumerate(sorted1["train"]):
#     avg_exp_train.append(avg_trial_time(exp,i))
    
# print("average trial tuning phase time", avg_exp_train)



def convert_string_timestamps(sorted):
    for i,exp in enumerate(sorted["train"]):
        for train in exp:
            train["start_time"] = toTime(train["start_time"])
            train["end_time"]= toTime(train["end_time"])

    for i,exp in enumerate(sorted["validate"]):
        for train in exp:
            train["start_time"] = toTime(train["start_time"])
            train["end_time"]= toTime(train["end_time"])

#converting string time to datetime format 





# calculates the maximal time when all trials were runing in parrallel
# input train_times_array of one experiment
def max_parrallel_time(train_times_array,exp_num=0):
    train_times_array.sort(key=lambda x :x["start_time"])
    max_exp_overlap= float("-inf")
    max_overlaps_number = 0

    for x, train in enumerate(train_times_array):
        log.debug(train["start_time"],train["duration_sec"])
        min_train_overlap = float("inf")
        min_overlaps_number = 0
        for y, othertrain in enumerate(train_times_array):
            if(othertrain["start_time"] > train["end_time"]):
                log.debug(x,y,"x ended  befor y started no overlap")
            
            elif(train["start_time"] > othertrain["end_time"]):
                log.debug(x,y, "x started after y ended no overlap")
              
            
            elif(othertrain["start_time"] >= train["start_time"] and othertrain["start_time"] <= train["end_time"]):
                overlap = (train["end_time"]-othertrain["start_time"]).total_seconds()
                if(othertrain["end_time"] <= train["end_time"]):
                    overlap-= (train["end_time"] - othertrain["end_time"]).total_seconds()
                log.debug(f"{x} {y} ovelap = {overlap}")

                if(y != x):
                    min_overlaps_number+=1

                if(min_train_overlap > overlap and x !=y):
                 
                    min_train_overlap=overlap

            
            else:
            
                log.debug(x,y,"already expressed by" ,y,x ,  "overlap =",overlap)
                # overlap = othertrain["duration_sec"] - (train["start_time"]-othertrain["start_time"]).total_seconds()
                # if(min_train_overlap > overlap and x !=y and overlap > 0):
                #     min_train_overlap=overlap   
   
   
        #if we found the higher number of overlaps we automaticly want also the acording overlap time not importatn if it was longer or shorter
        if(min_overlaps_number > max_overlaps_number):
            max_overlaps_number = min_overlaps_number
            max_exp_overlap = min_train_overlap 

        #if the number of overlaps is  equel to last highes number of overlaps
        #then we need to check if the overlap time was higher than the list on if not than we do not do antything
        if(min_overlaps_number == max_overlaps_number and max_exp_overlap < min_train_overlap and min_train_overlap != float("inf")):
            max_exp_overlap = min_train_overlap 
        
   #if there was no overlap 
    if(max_exp_overlap == float("-inf")):
        return 0,0    
   
    return max_exp_overlap,max_overlaps_number + 1 





# calculates time from timestamp of first initialised trial to end train time timestamp of last trial
# input train_times_array of one experiment
def trials_execution_time(train_times_array):

    train_times_array.sort(key=lambda x :x["start_time"])
    first_start = train_times_array[0]["start_time"]
    train_times_array.sort(key=lambda x :x["end_time"])
    last_end = train_times_array[-1]["end_time"]
    return (last_end - first_start).total_seconds()

def trials_validation_time(validation_times_array):
    return trials_execution_time(validation_times_array)


# calculates total time of trials execution
# input train_times_array of one experiment
def total_trials_execution_time(train_times_array):
    return sum( x["duration_sec"]  for x in train_times_array )

def total_trials_validation_time(validation_times_array):
    return total_trials_execution_time(validation_times_array)



def first_trial_initialization_time(train_times_array,run_start_time):
    

    train_times_array.sort(key=lambda x :x["start_time"])
    first_trial_init = train_times_array[0]

    
    print(run_start_time,first_trial_init["start_time"])
    return (first_trial_init["start_time"]- (run_start_time)).total_seconds() 

###new
def first_finished_trial_time(validation_times_array,run_start_time):

    validation_times_array.sort(key=lambda x :x["end_time"])
    first_trial_finish = validation_times_array[0]

    return (first_trial_finish["end_time"]- (run_start_time)).total_seconds() 

def last_trial_initialization_time(train_times_array,run_start_time):
    
   
    train_times_array.sort(key=lambda x :x["start_time"])
    last_trial= train_times_array[-1]
    


    return (last_trial["start_time"] - (run_start_time)).total_seconds() 

def avg_trial_initialization_time(train_times_array,run_start_time):
 
    return mean( ( trial["start_time"] - (run_start_time) ).total_seconds()  for trial in train_times_array)


def metrics_collection_time(train_times_array,run_end_time):

    train_times_array.sort(key=lambda x :x["end_time"])
 
    last_trial= train_times_array[-1]
    #print( " run end time",  (run_end_time),"last ended  trial",last_trial , "==" , (  (run_end_time)- last_trial["end_time"]).total_seconds()  )

    return ( run_end_time- last_trial["end_time"] ).total_seconds() 

def total_experiment_time(deploy_start_time,collect_benchmar_metrics_end_time):
    return ((collect_benchmar_metrics_end_time) - (deploy_start_time)).total_seconds()


def generate_all_metrics(data,sort_by):
    sorted = sort_experiments(data,sort_by)
    convert_string_timestamps(sorted)

  
    
    
    metrics = {
        "max_train_overlap_time":[],
        "max_train_overlaps_number":[],
        "total_trials_validation_time":[],
        "first_trial_initialization_time":[],
        "total_trials_execution_time":[],
        "trials_validation_phase_time":[],
        "trials_execution_phase_time":[],
        "avg_trial_execution_time":[],
        "avg_trial_validation_time":[],
        "avg_trial_initialization_time":[],
        "last_trial_initialization_time":[],
        "metrics_collection_time":[],
        "total_experiment_time":[],
        "first_finished_trial_time":[],
        "experiment_time":0


    }
    print("Metricsss")
    for metric in metrics:
        print("\subsection{"+ metric + "} \label{"+ metric+ "}")

    phases_durations = get_phases_durations(sorted)
    t = 0
    for exp_num,exp in enumerate(sorted["resources"]):
        print(exp)
        validation_times = sorted["validate"][exp_num]
        train_times = sorted["train"][exp_num]
        max_train_overlap_time, max_train_overlaps_number = max_parrallel_time(train_times)

        metrics["max_train_overlap_time"].append(max_train_overlap_time)
        metrics["max_train_overlaps_number"].append(max_train_overlaps_number)
        metrics["total_trials_validation_time"].append(total_trials_validation_time(validation_times))
        metrics["first_trial_initialization_time"].append(first_trial_initialization_time(train_times,sorted["run"][exp_num]["start_time"]))
        metrics["total_trials_execution_time"].append(total_trials_execution_time(train_times))
        metrics["trials_validation_phase_time"].append(trials_validation_time(validation_times))
        metrics["trials_execution_phase_time"].append(trials_execution_time(train_times))
        metrics["avg_trial_execution_time"].append(avg_trial_time(train_times,exp_num))
        metrics["avg_trial_validation_time"].append(avg_trial_time(validation_times,exp_num))

        metrics["last_trial_initialization_time"].append(last_trial_initialization_time(train_times,sorted["run"][exp_num]["start_time"]))
        metrics["first_finished_trial_time"].append(first_finished_trial_time(train_times,sorted["run"][exp_num]["start_time"]))
        metrics["avg_trial_initialization_time"].append(avg_trial_initialization_time(train_times,sorted["run"][exp_num]["start_time"]))
        metrics["metrics_collection_time"].append(metrics_collection_time(validation_times,sorted["run"][exp_num]["end_time"]))
        exptime = total_experiment_time(sorted["deploy"][exp_num]["start_time"], sorted["collect_benchmark_metrics"][exp_num]["end_time"])
        
        metrics["total_experiment_time"].append(exptime)

   # add last trial initialization: ö
   # avg initialization time ö
   # metrics collection time  last validation => end of the run Ö
   #experiment duration Ö
   # first finished trial 
   # wyliczyc ile to wszystko trwalo 
    metrics["experiment_time"] = t
    return  {sort_by:sorted[sort_by]} |  phases_durations | metrics




    

    




time_string = "2022-11-30 10:55:20.886185"
format =  "%Y-%m-%d %H:%M:%S.%f"
result = datetime.strptime(time_string,format)

start_time  = datetime.strptime( "2022-11-30 10:50:44.712740",format)
end_time = datetime.strptime("2022-11-30 10:51:57.792977",format)

roz = end_time-start_time

print(start_time,end_time, type(roz.total_seconds()))
#print(json.dumps(sorted["train"], indent=4))

# # Throuput max parallelzation time
# for i,train_array in enumerate(sorted["train"]):
#     #sorting acording to the start times
#     max_exp_overlap, max_overlaps_number = max_parrallel_time(train_array,i)
#     tet = trials_execution_time(train_array)
#     ttext= total_trials_execution_time(train_array)
#     fti = first_trial_initialization_time(i)
#     print(f'expnr {i} {max_exp_overlap} and {max_overlaps_number} vs avg-run-time {avg_exp_train[i]} tet {tet}  fti {fti} ttext {ttext}  {sorted["run"][i]["duration_sec"]}')









############################################################################################
#Tunning scalability There is 1 version
# Variabel: Trials number [1,2,4,6,8,10,12,14,16,18,20,22]
sort_by = "jobsCount"
metrics_to_plot = {
    # f"{sort_by}":{
    #     "title":"Job count",
    #     "x-label":"Jobs Count",
    #     "y-label":"Jobs Count",
    #     "refrence":"",
    #     "grid":"true",

    # },
     "run":{
        "title":"Duration of the tuning phase (run fuction)",
        "y-label":"Tuning phase time",
        "refrence":"",
        "grid":"true",
    },
     "avg_trial_execution_time":{
        "title":"Average duration of trial training",
        "y-label":"Average trial traing time",
        "refrence":"",
        "grid":"true",
    },
     "first_trial_initialization_time":{
        "title":"Time needed for initialization of first trial training",
        "y-label":"first trial initialization time",
        "refrence":"",
        "grid":"true",
    },
    "first_finished_trial_time":{
        "title":"Time needed for the first trial to be finished",
        "y-label":"first finished trial time",
        "refrence":"",
        "grid":"true",
    },
    "last_trial_initialization_time":{
        "title":"Time needed for initialization of the last trial training",
        "y-label":"last trial initialization time",
        "refrence":"",
        "grid":"true",
    },

    "avg_trial_initialization_time":{
        "title":"Average Time needed for initialization of  trials training",
        "y-label":"avg trial initialization time",
        "refrence":"",
        "grid":"true",
    },
    "metrics_collection_time":{
        "title":"time needed for collection of all trial metrics",
        "y-label":"metrics_collection_time",
        "refrence":"",
        "grid":"true",
        "description":"Time from ending of last validation to the end of the run phase"
    },



     "max_train_overlap_time":{
        "title":"Maximal Duration of parallel execution of trials trainig ",
        "y-label":"max train overlap time",
        "refrence":"",
        "grid":"true",
    },
    "max_train_overlaps_number":{
        "title":"Maximal number of trials that were  runing in Parallel",
        "y-label":"max number of trials run in parrallel",
        "refrence":"",
        "grid":"true",
    },
    "total_trials_validation_time":{
        "title":"Summed time of all trials validations",
        "y-label":"trials validation times sum",
        "refrence":"",
        "grid":"true",
    },
   
    "total_trials_execution_time":{
        "title":"Summed time of all trials trianing",
        "y-label":"trials training times sum",
        "refrence":"",
        "grid":"true",
    },
    "trials_validation_phase_time":{
        "title":"Time from begining of first validation to the end of last one",
        "y-label":"trials validation phase time",
        "refrence":"",
        "grid":"true",
    },
    "trials_execution_phase_time":{
        "title":"Time from begining of first trial training to the end of last one",
        "y-label":"trials training phase time",
        "refrence":"",
        "grid":"true",
    },
   
    "avg_trial_validation_time":{
        "title":"Average duration of trial validation",
        "y-label":"Average trial validation time",
        "refrence":"",
        "grid":"true",
    },
     "total_experiment_time":{
        "title":"Duration of whole experiment from deploy till end",
        "y-label":"Experiment duration",
        "refrence":"",
        "grid":"true",
    },


}

print("\n")


def plot_metrics_from_yaml(json_path ,latex_string,variabel = ""):
    

    with open(f"{json_path}.json","r") as f:
         exp_json =  json.load(f)

    exp_array = exp_json["experiments"]
    repetitions = exp_json["repetitions"]
    json_id = exp_json["json_id"]
    limitation = ""


    print(json.dumps(exp_json, indent=4))

    latex_string+= "\n\section{" + "section_name" + "}\label{sec:moti}\n" 
    latex_string+= variabel
    latex_string+="\n"   

   
    # latex_string = f' {katib["experiment_time"]}, {polyaxon["experiment_time"]}, ' + latex_string
    # # print(json.dumps(tuning_polyaxon, indent=4))
    # x = katib[sort_by]
    # x2 = polyaxon[sort_by]

    plots_folder = f"{json_path}"
    try:
        os.makedirs(plots_folder)
    except OSError:
        print ("Creation of the directory %s failed" % plots_folder)
    
    for exp in exp_array:
        variabels = exp["values"]
        if(exp["experiment_titel"] == "clean_up"):
            print("clean")
        
        elif(exp["experiment_titel"] == "deploy"):
            print("deploy")

        elif(exp["generatePlots"] ):
            print(exp["experiment_titel"])
            exp_titel = exp["experiment_titel"]
            sort_by =  exp["variabel"]
            x = exp["values"]
            katib_exp_data_reps = []
            polyaxon_exp_reps = []

            #geting metrics from each repetition         
            # for rep in [1]:
            for rep in range(1,repetitions + 1):
                katib_exp_data = load_data("../katib_k8s/benchmark__KatibBenchmark",json_id,exp_titel,rep)
                polyaxon_exp_data = load_data("../polyaxon_k8s/benchmark__PolyaxonBenchmark",json_id,exp_titel,rep)

                katib_exp_data_reps.append( generate_all_metrics(katib_exp_data,sort_by))
                polyaxon_exp_reps.append(generate_all_metrics(polyaxon_exp_data,sort_by))

            polyaxon = {}
            polyaxon_sorted = {}
            
            katib = {}
            katib_sorted = {}
           
            #everaging the experiment
            metrics_to_plot = exp_json["metrics_to_plot"][exp["experiment_titel"]]
            for metric in metrics_to_plot:
                katib_sorted[metric]=[]
                katib[metric] = []
                polyaxon[metric] = []
                polyaxon_sorted[metric] = []

                for k , var in enumerate(variabels):
                    arr_katib =  list(map(lambda x : x[metric][k],katib_exp_data_reps )) 
                    arr_polyaxon =  list(map(lambda x : x[metric][k],polyaxon_exp_reps )) 
                    arr_katib.sort()
                    arr_polyaxon.sort()

                    katib_sorted[metric].append(arr_katib)
                    katib[metric].append(mean(arr_katib))
                    polyaxon[metric].append(mean(arr_polyaxon))
                    polyaxon_sorted[metric].append(arr_polyaxon)



                    print(metric,var,arr_katib,k)

            print("xd dziala")


            for metric in metrics_to_plot:
                for plot_num , plot in enumerate(metrics_to_plot[metric]):
                  
                

                    fig, ax = plt.subplots()
            
                
                
                    ax.set_xlabel(sort_by)
                    ax.set_ylabel(plot["y-label"])
                    ax.set_title(plot["title"])

                    x_lim = plot.get("x_lim","")
                    if(x_lim):
                        plt.xlim(**x_lim)

                    y_lim = plot.get("y_lim","")
                    if(y_lim):
                        plt.ylim(**y_lim)


                    ax.plot(x,katib[metric],"r", marker="o")
                
                    ax.plot(x,polyaxon[metric],"b",marker="o")
                    refrence = plot.get("refrence","")
                    refrence_titel = plot.get("refrence_title","")
                    refrence_marker = plot.get("refrence_marker",",")
                    if(refrence):
                        ax.plot(x,refrence,"g",marker=refrence_marker)
                        ax.legend(["Katib","Polyaxon",refrence_titel])
                    else:
                        ax.legend(["Katib","Polyaxon"])

                    
                    y_ticks = plot.get("y_ticks","")
                    if(y_ticks):
                        plt.yticks(y_ticks,y_ticks)
                    
                    x_tickts = plot.get("x_ticks",variabels)
                    if(x_tickts):
                        plt.xticks(x_tickts,x_tickts)
                    
                                    
                    # variabels    = list(range(0,22,1))
                    
                
                    ax.grid()
                    
                    print(variabels)

                    exp_folder = f"{plots_folder}/{exp_titel}"
                    
                    try: 
                        os.mkdir(exp_folder)
                    except OSError:
                        print (" Creation of the directory %s failed" % plots_folder)
                    fig.savefig(f"{exp_folder}/{limitation}{sort_by}-{metric}{plot_num}.png")

                    latex_string+= "\subsection{" + plot["title"] + "}\label{plot:" + f"{limitation}{sort_by}-{metric}" + "}\n" 
                    latex_string+= "Some text\n" 
                    latex_string+= "\n" 
                    latex_string+= "\n" 
                    latex_string+= "\\begin{figure}[h]\n" 
                    latex_string+= "    \centering\n" 
                    latex_string+= "    \includegraphics[width=1\\textwidth]{img/plots/" + f"{limitation}{sort_by}-{metric}.png"+ "}\n" 
                    latex_string+= "    \caption{Tittel decription}\n" 
                    latex_string+= "    \label{fig:mesh1}\n" 
                    latex_string+= "\end{figure}\n" 
                    latex_string+= "\\newpage\n" 
                    latex_string+= "\n" 
                    latex_string+= "\n" 
 
    return latex_string
        #plt.show()
plot_metrics_from_yaml("5_resources_1000","")
plot_metrics_from_yaml("4_resources_500","")
plot_metrics_from_yaml("1_tuning","")


latex_string= "\\chapter{Plots}\n"

depl = { "deploy":{
        "title":"Time needed for deploying",
        "y-label":"Deploy phase time",
        "refrence":"",
        "grid":"true",
    }}

section_name = "Deploy times"
limitation = ""
# latex_string = plot_metrics_from_folders("deploy_katib","deploy_polyaxon",sort_by,depl,section_name,latex_string,limitation)

#plot_metrics_from_folders("resources_katib/1000m","resources_polyaxon/1000m","limitCpuTotal",metrics_to_plot)

#plot_metrics_from_folders("resources_katib/1000m","resources_polyaxon/1000m","limitCpuTotal",metrics_to_plot)




############################################################################################
#Resources scalability. There are 6 versions
#Experimental Variabel: Total aviabel CPU [4,6,8,10,12,14,16,18,20,22,24]
#             
#Versions variabels:   trials_number x cpu_limit_pro_trial 
#                            [10,20] x [500m,1000m,2000m]   => 6 Versions





############################################################################################
#Worker scalability. There is one version
#Experimental variabel: cpu_limit_pro_trial in m [400,600,800,1000,1200,1400,1600,1800,2000,2200]
#
# const: Total aviabel CPU 28, trialsnumber 10

print(latex_string)


print("gunwo"[:-1])

# brauche etwa 45 min pro experiment beim leeren cluster 