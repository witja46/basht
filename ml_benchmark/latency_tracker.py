import os
from datetime import datetime, timedelta
from abc import ABC, abstractmethod
from uuid import uuid4
from sqlalchemy import create_engine, MetaData, Table, insert
import psycopg2


class Tracker(ABC):

    @abstractmethod
    def track(self, metric):
        pass


class LatencyTracker(Tracker):

    def __init__(self, connection_string: str = None) -> None:
        if connection_string:
            self.engine = self._create_engine(connection_string)

    def _create_engine(self, connection_string):
        try:
            engine = create_engine(connection_string, echo=True)
        except psycopg2.Error:
            raise ConnectionError("Could not create an Engine for the Postgres DB.")
        return engine

    def track(self, latency_obj):
        # TODO: test this shit
        metadata = MetaData(bind=self.engine)
        latency = Table("latency", metadata, autoload_with=self.engine)
        with self.engine.connect() as conn:
            stmt = insert(latency).values(latency_obj.to_dict())
            result = conn.execute(stmt)
        print(result)


# TODO: decorator for trial latencies?
class Latency:

    def __init__(self, func) -> None:
        # TODO: how to maintain identifiability for one trial?
        self.name: str = func.__name__
        self.process_id = os.getpid()
        try:
            self.obj_hash = hash(func.__self__)
        except AttributeError as e:
            print(e)
            raise AttributeError("Functions need to be part of a class in order to measure their latency.")
        self.id = f"pid_{self.process_id}__name_{self.name}__objHash_{self.obj_hash}__id_{uuid4()}"
        self.start_time: float = None
        self.end_time: float = None
        self.duration: float = None

    def to_dict(self):
        latency_dict = dict(
            id=self.id,
            name=self.name,
            start_time=self.start_time,
            end_time=self.end_time,
            duration=self.duration
        )
        latency_dict = {key: self._convert_times_to_float(value) for key, value in latency_dict.items()}

        return latency_dict

    def __enter__(self):
        self.start_time = datetime.now()
        return self

    def __exit__(self, *args):
        self.end_time = datetime.now()
        self._calculate_duration()

    def _calculate_duration(self):
        self.duration = self.end_time - self.start_time

    def _convert_times_to_float(self, value):
        if isinstance(value, timedelta):
            return value.total_seconds()
        else:
            return str(value)


# decorators overwrite a decorated function once it is passed to the compiler
def latency_decorator(func):
    def latency_func(*args, **kwargs):
        func.__self__ = args[0]
        with Latency(func) as latency:
            result = func(*args, **kwargs)
        latency_tracker = LatencyTracker(connection_string=func.__self__.metrics_storage_address)
        latency_tracker.track(latency)
        func.__self__ = None
        return result
    return latency_func


if __name__ == "__main__":

    from ml_benchmark.metrics_storage import MetricsStorage
    import docker
    import json

    storage = MetricsStorage()

    class Test:
        metrics_storage_address = MetricsStorage.connection_string

        def __init__(self) -> None:
            pass

        @latency_decorator
        def a(self, b):
            return b

        @latency_decorator
        def c(self, b):
            return b

    try:
        storage.start_db()
        testclass = Test()
        testclass.a(2)
        testclass.c(2)
        result = storage.get_benchmark_results()
        storage.stop_db()
    except docker.errors.APIError:
        storage.stop_db()
    print(json.dumps(result))
