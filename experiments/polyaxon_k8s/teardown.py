import os
from time import sleep

res = os.popen("kubectl delete --wait=false  namespace polyaxon ").read()
print(res)
sleep(2)
res = os.popen("kubectl delete --wait=false crd operations.core.polyaxon.com ").read()
print(res)
sleep(4)
res = os.popen('kubectl patch  crd/operations.core.polyaxon.com  -p  \'{"metadata":{"finalizers":null}}\'').read()
print(res)
