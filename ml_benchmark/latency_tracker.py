from dataclasses import dataclass, asdict
from datetime import datetime, timedelta


class LatencyTracker:

    def __init__(self) -> None:
        self.recorded_latencies = []

    def track(self, latency):
        self.recorded_latencies.append(latency)

    def get_recorded_latencies(self):
        return [latency.to_dict() for latency in self.recorded_latencies]


# TODO: decorator for trial latencies?
@dataclass
class Latency:

    name: str
    start_time: float = None
    end_time: float = None
    duration: float = None

    def to_dict(self):
        latency_dict = asdict(self)
        latency_title = latency_dict.pop("name")
        latency_dict = {key: self._convert_times_to_float(value) for key, value in latency_dict.items()}

        return {
            latency_title: latency_dict
        }

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
            return value.timestamp()


def latency_decorator(func):
    def latency_func(*args, **kwargs):
        with Latency(f"trail__{func.__name__}") as latency:
            result = func(*args, **kwargs)
        result["latency"] = latency.to_dict()
        return result
    return latency_func


if __name__ == "__main__":

    def a(b):
        return b
    with Latency(a.__name__) as latency:
        a(2)
    print(latency.duration)
    print(latency.to_dict())
