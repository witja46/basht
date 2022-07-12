import pytest
from ml_benchmark.latency_tracker import latency_decorator
from ml_benchmark.workload.objective import Objective, ObjectiveHelper


@pytest.fixture
def objective():
    class TestObjective(Objective, ObjectiveHelper):

        def __init__(self) -> None:
            super(TestObjective, self).__init__()

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
