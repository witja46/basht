import logging
from ml_benchmark.latency_tracker import Tracker #TODO: move to utils
from ml_benchmark.metrics import Result
from ml_benchmark.metrics_storage import MetricsStorageStrategy

class ResultTracker(Tracker):
    def __init__(self,resouce_store=MetricsStorageStrategy):
        self.store = resouce_store()
        self.store.setup()

    def track(self, objective, value, measure):
        r = Result(objective=objective)
        r.value = value
        r.measure = measure
        try:
            self.store.store(r,table_name="classification_metrics")
        except Exception as e:
            logging.warn(f"failed to store result {e}")
