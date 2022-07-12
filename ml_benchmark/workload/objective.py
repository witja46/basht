from abc import ABC, abstractmethod
import os

from ml_benchmark.metrics_storage import MetricsStorage


class Objective(ABC):

    """
    Interface for a training, validation and test procedure of a model.
    """



    @abstractmethod
    def train(self):
        pass

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def test(self):
        pass


class ObjectiveHelper:

    def __init__(self) -> None:
        # need possibility to set dynamically - public IP if ssh connect
        self.metrics_storage_adress = self._get_db_connection_string()

    def _get_db_connection_string(self):
        connection_string = os.environ.get("METRICS_DB_ADRESS")
        if not connection_string:
            connection_string = MetricsStorage.connection_string
        return connection_string
