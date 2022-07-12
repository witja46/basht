from abc import ABC, abstractmethod
import os

from ml_benchmark.config import MetricsStorageConfig


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
        """
        The ObjectiveHelper serves as a Helper Class to setup the objective for a trial.
        The Objective can be performed on a different execution environment, than the benchmark itself.
        Therefore it needs to be ensured, that necessary information for tracking metrics are handed over to
        the objective.
        """
        # TODO: need possibility retrieve automatically
        self.metrics_storage_adress = self._get_db_connection_string()

    def _get_db_connection_string(self):
        """
        Gets the connection string of the database from an environment variale. If the environment variable is
        not set, the default value is retrieved from the MetricsStorageConfig as per assumption the objective
        is exectued on within the same environment. If not please set "METRICS_DB_ADRESS" as a environment
        variable. Otherwise the tracker will not be able to connect to the metrics storage.

        Returns:
            _type_: _description_
        """
        connection_string = os.environ.get("METRICS_DB_ADRESS")
        if not connection_string:
            connection_string = MetricsStorageConfig.connection_string
        return connection_string
