import pytest
from ml_benchmark.metrics_storage import MetricsStorage
from ml_benchmark.latency_tracker import latency_decorator


@pytest.fixture
def objective():
    class TestObjective:
        metrics_storage_address = MetricsStorage.connection_string

        def __init__(self) -> None:
            pass

        @latency_decorator
        def train(self):
            pass

        @latency_decorator
        def validate(self):
            return 0.5

        @latency_decorator
        def test(self):
            return {"score": 0.5}
    return TestObjective
