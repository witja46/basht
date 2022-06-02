#! python3
import logging
from datetime import datetime, timedelta
from tkinter.messagebox import NO
import numpy as np
import pandas as pd
import base64

from torch import FunctionSchema



class Metrics():
    def __init__(self,fields:list,fieldnames:list) ->None:
        self.fields = fields
        self.fieldnames = fieldnames
        if len(fields) != len(fieldnames):
            raise ValueError("Fields and fieldnames must have the same length")

        self.run_start = None
        self.setup_start = None
        self.setup_end = None
        self.run_end = None
        self.trail_times = []
        self.resultcollection_start = None
        self.resultcollection_end  = None
        self.test_start = None
        self.test_end = None
        self.collect_end = None
        self.undeploy_end = None

    def setup_time(self) -> timedelta:
        return self.setup_end - self.run_start

    def optimization_time(self) -> timedelta:
        return self.test_end - self.setup_start

    def addTrailTime(self, load: timedelta,train:timedelta,validate:timedelta) -> None:
        self.trail_times.append([load,train,validate])

    def evaluate_time(self) ->timedelta:
        return self.test_end - self.resultcollection_start

    def trail_times(self) -> np.array:
        arr = np.array(self.trail_times)
        return arr.sum(axis=1)

    def load_times(self) -> np.array:
        arr = np.array(self.trail_times)
        return arr[:,0]

    def train_times(self) -> np.array:
        arr = np.array(self.trail_times)
        return arr[:,1]

    def validate_times(self) -> np.array:
        arr = np.array(self.trail_times)
        return arr[:,2]

    def runtime(self) -> timedelta:
        return self.setup_start-self.run_start + self.optimization_time() + self.undeploy_end - self.collect_end

    def asPanda(self) -> pd.DataFrame:
        """
            asPanda(): returns an exploed view of all measumentes, containg all key measurmentes as columns replicated for each trail
        """
        columns = self.fieldnames + ["trail_id","setup_start","setup_end","run_start","run_end","collect_start","collect_end","test_start","test_end","undeploy_start","undeploy_end","setup_time","optimization_time","evaluate_time","total_runtime","load","train","validate"]

        basevalues = [self.setup_start,self.setup_end,self.run_start,self.run_end,self.resultcollection_start,self.resultcollection_end,self.test_start,self.test_end,self.collect_end,self.undeploy_end,self.setup_time(),self.optimization_time(),self.evaluate_time(),self.runtime()]

        data = []
        for i in range(len(self.trail_times)):
            values = self.fields+ + [i] + basevalues + self.trail_times[i]
            data.append(values)

        return pd.DataFrame(data,columns=columns)

    def asCompactPanda(self,identifier:str) -> pd.DataFrame:
        columns = self.fieldnames + ["id","setup_start","setup_end","run_start","run_end","collect_start","collect_end","test_start","test_end","undeploy_start","undeploy_end","setup_time","optimization_time","evaluate_time","total_runtime"]
        basevalues = self.fields + [identifier] +[self.setup_start,self.setup_end,self.run_start,self.run_end,self.resultcollection_start,self.resultcollection_end,self.test_start,self.test_end,self.collect_end,self.undeploy_end,self.setup_time(),self.optimization_time(),self.evaluate_time(),self.runtime()]

        data = []
        for i in range(len(self.trail_times)):
            values = [identifier] + self.trail_times[i]
            data.append(values)

        return pd.DataFrame(basevalues,columns=columns), pd.DataFrame(data,columns=["id","load","train","validate"])

    def store(self, fname: str) -> None:
        """
            store(fname:str): stores the metrics in the file fname
        """
        df = self.asPanda()
        df.to_csv(fname)


class BenchmarkRunner():

    def __init__(self, benchName, config) -> None:
        """
            benchName: uniqueName of the bechmark, used in logging
            config: configuration object
        """

        self.benchName = benchName
        #generate a unique name from the config
        base64_bytes = base64.b64encode(str(config).encode('ascii'))
        self.configName = str(base64_bytes, 'ascii')

        self.rundate = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        #perpare logger
        self.logger = Metrics([self.benchName,self.configName,self.rundate],["name","config","date"])

    def deploy(self) -> None:
        """
            With the completion of this step the desired architecture of the HPO Framework should be running on a platform, e.g,. in the case of Kubernetes it referes to the steps nassary to deploy all pods and services in kubernetes.
        """
        pass

    def setup(self):
        pass

    def run(self,m:Metrics) -> str:
        """
            Executing the hyperparameter optimization on the deployed platfrom.
            use the metrics object to collect and store all measurments on the workers.
        """
        pass

    def collect_benchmark_metrics(self):
        """
            Describes the collection of all gathered metrics, which are not used by the HPO framework (Latencies, CPU Resources, etc.). This step runs outside of the HPO Framework.
            Ensure to optain all metrics loggs and combine into the metrics object.
        """
        pass

    def undeploy(self):
        """
            The clean-up procedure to undeploy all components of the HPO Framework that were deployed in the Deploy step.
        """
        pass

    def test(self):
        pass

    def collect_trial_results(self):
        pass

    def main(self,fname:str):
        self.logger.run_start = datetime.now()
        self.deploy()
        self.logger.setup_start = datetime.now()
        self.run(self.logger)
        self.logger.run_end = datetime.now()

        self.logger.resultcollection_start = datetime.now()
        self.collectMetrics()
        self.logger.resultcollection_end = datetime.now()
        self.undeploy()
        self.logger.undeploy_end = datetime.now()

        if fname is not None:
            self.logger.store(fname)
