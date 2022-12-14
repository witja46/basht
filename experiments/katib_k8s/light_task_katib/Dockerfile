FROM python:3.9-slim

RUN pip install pip --upgrade


COPY experiments/katib_k8s  experiments/katib_k8s
COPY setup.py setup.py
COPY ml_benchmark ml_benchmark



RUN pip install -e .

CMD ["python", "experiments/katib_k8s/light_task_katib/task.py"]