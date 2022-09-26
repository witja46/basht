import json
import logging
import os
from datetime import datetime, timedelta
from uuid import uuid4
import socket
from dataclasses import dataclass, asdict


@dataclass
class Metric:
    """
    Metric Parentclass. Creates a unique identifier for every metric and gathers basic information.
    """
    metric_id = ""

    def add_to_id(self, id_addition):
        self.metric_id = self.metric_id + f"__{id_addition}"

    def to_dict(self):
        return asdict(self)


class NodeUsage(Metric):
    def __init__(self, node_id):
        super().__init__()
        self.node_id = node_id

        self.add_to_id(f"{self.node_id}")

        self.timestamp = None
        self.cpu_usage = None
        self.memory_usage = None
        self.network_usage = None
        self.accelerator_usage = None
        self.wattage = None
        self.processes = None

    def to_dict(self):
        node_dict = dict(
            metric_id=self.metric_id,
            timestamp=self.timestamp,
            cpu_usage=self.cpu_usage,
            memory_usage=self.memory_usage,
            network_usage=self.network_usage,
            wattage=self.wattage,
            processes=int(self.processes),
        )
        if self.accelerator_usage:
            node_dict["accelerator_usage"] = self.accelerator_usage

        return {key: _convert_datetime_to_unix(value) for key, value in node_dict.items()}
    
    def __repr__(self):
        return str(self.to_dict())


class Result(Metric):
    def __init__(self, objective):
        super().__init__()

        # add fingerprinting data to self
        self.fp = _fingerprint(self,objective)
        self.timestamp = datetime.now().ctime()
        self.value = None
        self.measure = None

        self.hyperparameters = None
        self.classification_metrics = None

    def to_dict(self):
        return dict(
            metric_id=self.metric_id,
            timestamp=self.timestamp,
            value=self.value,
            hyperparameters=json.dumps(self.hyperparameters, indent=None),
            classification_metrics=json.dumps(self.classification_metrics,indent=None),
            measure=self.measure,
            **self.fp
        )
        


def _fingerprint(metric,func):
    process_id = os.getpid()
    # inject the NODE_NAME (from the environment) - should be availble in containerized environments
    if os.getenv("NODE_NAME"):
        hostname = f'{os.getenv("NODE_NAME")}_{socket.gethostname()}'
    else:
        hostname = f'BARE_{socket.gethostname()}'
    metric.add_to_id(f"id_{uuid4()}__pid_{process_id}__hostname_{hostname}")

    obj_hash = 0
    try:
        obj_hash = hash(func.__self__)
    except AttributeError as e:
        logging.warn(f"fingerprinting error {e}")
        raise AttributeError("Functions need to be part of a class in order to measure their latency. {e}")

    return {
        "process_id": process_id,
        "hostname": hostname,
        "obj_hash": obj_hash,
    }


class Latency(Metric):

    def __init__(self, func) -> None:
        """The latency of provided the function gives the duration of the start_time and end_time of the provided
        function.
        The id is generated from:
            * the process the function is running on, the name of the function
            * the object which the function is a class method of
            * a randomly generated number, to maintain uniqueness of the id.

        The object hash shall identify a single trail as it is assumed that a trail used 'train' and 'test'
        from the same Objective object.

        Args:
            func (_type_): _description_

        Raises:
            AttributeError: _description_
        """
        super().__init__()
        #TODO: make each id filed also availible as a column
        fp = _fingerprint(self,func)
        obj_hash = fp["obj_hash"]
        function_name: str = func.__name__
        self.function_name = function_name
        self.add_to_id(f"function-name_{function_name}__objHash_{obj_hash}")

        self.start_time: float = None
        self.end_time: float = None
        self.duration_sec: float = None

    def to_dict(self):
        latency_dict = dict(
            metric_id=self.metric_id,
            function_name=self.function_name,
            start_time=self.start_time,
            end_time=self.end_time,
            duration_sec=self.duration_sec
        )
        # latency_dict.update(super().to_dict())
        latency_dict = {key: _convert_times_to_float(value) for key, value in latency_dict.items()}

        return latency_dict

    def __enter__(self):
        """Entering point of the context manager.

        Returns:
            _type_: _description_
        """
        self.start_time = datetime.now()
        return self

    def __exit__(self, *args):
        """
        Exit point of the context manager.
        """
        self.end_time = datetime.now()
        self._calculate_duration()

    def _calculate_duration(self):
        self.duration_sec = self.end_time - self.start_time


def _convert_times_to_float(value):
    if isinstance(value, timedelta):
        return value.total_seconds()
    else:
        return str(value)

def _convert_datetime_to_unix(value):
    if isinstance(value, datetime):
        return value.ctime()
    else:
        return str(value)