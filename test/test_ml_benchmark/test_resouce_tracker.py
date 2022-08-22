
import logging
from ml_benchmark.resource_tracker import ResourceTracker, LoggingResouceStore
def test_resouce_tracker():


    import time
    logging.basicConfig(level=logging.DEBUG)
    rt = ResourceTracker(prometheus_url="http://130.149.158.143:30041", resouce_store=LoggingResouceStore)
    rt.start()
    time.sleep(ResourceTracker.UPDATE_INTERVAL * 15)
    rt.stop()
    print(rt.store.log)
    assert rt.store.log != []