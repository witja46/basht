from abc import ABC, abstractmethod

from ml_benchmark.metrics_storage import MetricsStorage


class Objective(ABC):

    """
    Interface for a training, validation and test procedure of a model.
    """

    # need possibility to set dynamically - public IP if ssh connect
    metrics_storage_address = MetricsStorage.connection_string # create on object init

    @abstractmethod
    def train(self):
        pass

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def test(self):
        pass
