from datetime import timedelta
import numpy as np
import pandas as pd


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
