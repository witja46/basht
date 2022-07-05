from ray import tune


def raytune_func(config):
            """The function for training and validation, that is used for hyperparameter optimization.
            Beware Ray Synchronisation: https://docs.ray.io/en/latest/tune/user-guide.html

            Args:
                config ([type]): [description]
            """
            objective = config.get("objective")
            hyperparameters = config.get("hyperparameters")
            objective.set_hyperparameters(hyperparameters)
            # these are the results, that can be used for the hyperparameter search
            objective.train()
            validation_scores = objective.validate()
            tune.report(macro_f1_score=validation_scores["macro avg"]["f1-score"])

analysis = tune.run(
    raytune_func,
    config=dict(
        objective=objective,
        hyperparameters=grid,
        ),
    sync_config=tune.SyncConfig(
        syncer=None  # Disable syncing
        ),
    local_dir="/volume/ray_results",
    resources_per_trial={"cpu": resources["cpu"]}
)
