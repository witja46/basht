FROM python:3.9-slim

RUN pip install pip --upgrade
RUN pip install polyaxon


COPY experiments/polyaxon_k8s  experiments/polyaxon_k8s
COPY setup.py setup.py
COPY ml_benchmark ml_benchmark



RUN pip install -e .

CMD ["python", "experiments/polyaxon_k8s/light_task_polyaxon/task.py"]