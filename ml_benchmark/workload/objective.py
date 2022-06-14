from abc import ABC, abstractmethod


class Objective(ABC):

    metrics_persistor_address = None

    @abstractmethod
    def train(self):
        pass

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def test(self):
        pass
