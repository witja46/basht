import multiprocessing
import time
from itertools import product
from multiprocessing import Pool, cpu_count

ctx = multiprocessing.get_context("spawn")


class GridSearch:

    def __init__(self, objective_cls, objective_args, grid, device, threads=None) -> None:
        """_summary_

        Args:
            objective (_type_): _description_
            grid (dict): Need to be a dict of iterables.
            device (str): pytorch device string
            threads (int, optional): Defaults to number of availible CPUS. Number of threads to use.
        """
        self.objective_cls = objective_cls
        self.objective_args = objective_args
        self.grid = self._generate_parameters(grid)
        self.device = device
        if threads:
            self.threads = threads
        else:
            self.threads = cpu_count()

    def _generate_parameters(self, grid):
        return product([dict(zip(grid, v)) for v in product(*grid.values())])

    def _run_objective(self, hyperparameter_config):
        job = TuneJob(self.objective_cls, self.objective_args, self.device, hyperparameter_config[0])
        score = job.main()
        return {'params': hyperparameter_config[0], 'score': score}

    def main(self):
        start = time.time()
        grid_search_score_dump = []
        if self.threads > 1:
            with ctx.Pool(self.threads) as p:
                grid_search_score_dump = p.map(self._run_objective, self.grid)
        else:
            for hyper_config in self.grid:
                grid_search_score_dump.append(self._run_objective(hyper_config))

        print(grid_search_score_dump)
        print(f'Grid search took {time.time() - start} seconds')


class TuneJob:
    def __init__(self, objective_cls, objective_args, device, hyperparameters) -> None:
        self.objective = objective_cls(**objective_args)
        self.device = device
        self.hyperparameters = hyperparameters

    def main(self):
        self.objective.set_hyperparameters(self.hyperparameters)
        self.objective.set_device(self.device)
        self.objective.train()
        return self.objective.validate()["macro avg"]["f1-score"]


if __name__ == "__main__":
    from ml_benchmark.mlp_objective import MLPObjective
    from ml_benchmark.mnist_task import MnistTask
    epochs = 5
    configuration = {
            "val_split_ratio": 0.2, "train_batch_size": 512, "val_batch_size": 128, "test_batch_size": 128}
    grid = dict(
            input_size=[28*28],
            learning_rate=[1e-4, 1e-2],
            weight_decay=[1e-6],
            hidden_layer_config=[[20], [10, 10]],
            output_size=[10])

    task = MnistTask()
    train_loader, val_loader, test_loader = task.create_data_loader(configuration)
    objective_cls = MLPObjective
    objective_args = dict(
        epochs=epochs,
        train_loader=train_loader,
        val_loader=val_loader,
        test_loader=test_loader
        )
    device = "cpu"
    grid_search = GridSearch(
        objective_cls=objective_cls, objective_args=objective_args, grid=grid, device=device, threads=2)
    grid_search.main()
