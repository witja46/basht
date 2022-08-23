
import logging
import os
import pytest
from ml_benchmark.resource_tracker import ResourceTracker, LoggingResouceStore
import requests

@pytest.fixture
def prometeus_url():
    url =  os.environ.get("PROMETHEUS_URL", "http://localhost:9090")
    try:
        resp = requests.get(url)
        if resp.status_code != 200:
            pytest.skip("Prometheus is availible")
    except Exception:
        pytest.skip("Could not connect to Prometheus.")
    
    return url



def test_resouce_tracker(prometeus_url):
    import time
    logging.basicConfig(level=logging.DEBUG)
    rt = ResourceTracker(prometheus_url=prometeus_url, resouce_store=LoggingResouceStore)
    rt.start()
    time.sleep(ResourceTracker.UPDATE_INTERVAL * 15)
    rt.stop()
    print(rt.store.log)
    assert rt.store.log != []

def test_resouce_tracker_with_namespace(prometeus_url):
    import time
    logging.basicConfig(level=logging.DEBUG)
    rt = ResourceTracker(prometheus_url=prometeus_url, resouce_store=LoggingResouceStore)
    rt.namespace = "optuna-study"
    rt.start()
    time.sleep(ResourceTracker.UPDATE_INTERVAL * 15)
    rt.stop()
    print(rt.store.log)
    assert rt.store.log != []