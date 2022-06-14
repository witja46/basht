from abc import ABC, abstractmethod

from ml_benchmark.metrics_storage import MetricsStorage


class Objective(ABC):

    # need possibility to set dynamically
    metrics_storage_address = MetricsStorage.connection_string

    @abstractmethod
    def train(self):
        pass

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def test(self):
        pass
