import os
import sys
from time import sleep
import optuna
from ml_benchmark.workload.mnist.mnist_task import MnistTask


def optuna_trial(trial):
    task = MnistTask(config_init={"epochs": 1})
    objective = task.create_objective()
    lr = trial.suggest_float("learning_rate", 1e-3, 0.1, log=True)
    decay = trial.suggest_float("weight_decay", 1e-6, 1e-4, log=True)
    objective.set_hyperparameters({"learning_rate": lr, "weight_decay": decay})
    objective.train()
    validation_scores = objective.validate()
    return validation_scores["macro avg"]["f1-score"]


if __name__ == "__main__":
    try:
        study_name = os.environ.get("STUDY_NAME")
        database_conn = os.environ.get("DB_CONN")
        study = optuna.create_study(
            study_name=study_name, storage=database_conn, direction="maximize", load_if_exists=True)
        study.optimize(optuna_trial, n_trials=5)
        # TODO: add small wait to avoid missing metrics
        sleep(5)
        sys.exit(0)
    except Exception:
        sys.exit(1)
