import optuna
import os

from ml_benchmark.workload.mnist.mnist_task import MnistTask


def optuna_trial(trial):
    """The function for training and validation, that is used for hyperparameter optimization.
    Beware Ray Synchronisation: https://docs.ray.io/en/latest/tune/user-guide.html

    Args:
        config ([type]): [description]
    """
    objective = MnistTask(config_init={"epochs": 1}).create_objective()
    hyperparameters = config.get("hyperparameters")
    objective.set_hyperparameters(hyperparameters)
    # these are the results, that can be used for the hyperparameter search
    objective.train()
    validation_scores = objective.validate()
    return validation_scores["macro avg"]["f1-score"]


if __name__ == "__main__":
    study_name = os.environ.get("STUDYNAME")
    database = os.environ.get("DB_CONN")
    study = optuna.create_study(study_name=os.environ.get())
