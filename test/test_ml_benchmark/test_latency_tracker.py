from ml_benchmark.latency_tracker import latency_decorator
from ml_benchmark.metrics_storage import MetricsStorage
import pytest
import docker
import json


def test_latency_decorator(objective):
    objective = objective()
    metrics_storage = MetricsStorage()

    try:
        metrics_storage.start_db()
        objective.train()
        objective.validate()
        objective.test()
        result = metrics_storage.get_benchmark_results()
        metrics_storage.stop_db()
    except docker.errors.APIError:
        metrics_storage.stop_db()

    assert isinstance(json.dumps(result), str)
