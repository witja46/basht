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
    """
    A Tracker that establishes a connection to the Latency Table in the postgres database. The LatencyTracker
    is used to write a latency into the postgres database.

    Args:
        Tracker (_type_): _description_
    """

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
        """
        Records a latency by writing it into a postgres database. First the table is retrieved, afterwards
        a connection is established and an INSERT statement is executed to save the results.

        Args:
            latency_obj (_type_): _description_
        """
        # TODO: test this shit
        metadata = MetaData(bind=self.engine)
        latency = Table("latency", metadata, autoload_with=self.engine)
        with self.engine.connect() as conn:
            stmt = insert(latency).values(latency_obj.to_dict())
            conn.execute(stmt)
        print(f"Latency Recorded! Latency: {latency_obj.to_dict()}")


# TODO: decorator for trial latencies?
class Latency:

    def __init__(self, func) -> None:
        """The latency of provided function gfives the duration of the start_time and end_time of the provided
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
        self.duration = self.end_time - self.start_time

    def _convert_times_to_float(self, value):
        if isinstance(value, timedelta):
            return value.total_seconds()
        else:
            return str(value)


# decorators overwrite a decorated function once it is passed to the compiler
def latency_decorator(func):
    """A Decorator to record the latency of the decorated function. Once it is recorded the LatencyTracker
    writes the result into the postgres databse.

    Args:
        func (_type_): _description_
    """
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
