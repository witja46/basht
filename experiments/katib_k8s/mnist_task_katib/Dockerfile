FROM python:3.9.6-slim

RUN pip install pip --upgrade
RUN pip install torch==1.10.2 torchvision==0.11.3
RUN pip install optuna==2.10.1

COPY experiments/katib_k8s  experiments/katib_k8s
COPY setup.py setup.py
COPY ml_benchmark ml_benchmark



RUN pip install -e .

CMD ["python", "experiments/katib_k8s/mnist_task_katib/task.py"]
