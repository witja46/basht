#TODO change to some slimer base image
FROM pytorch/pytorch:1.12.0-cuda11.3-cudnn8-runtime
#FROM python:3.9-slim

RUN pip install pip --upgrade

COPY experiments experiments
# COPY data data
COPY setup.py setup.py
COPY ml_benchmark ml_benchmark



RUN pip install -e .

CMD ["python", "experiments/katib_minikube/mnist_task/task.py"]
