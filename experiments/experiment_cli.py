import click
from experiments.vanilla_grid_search.vanilla_grid_search import VanillaGridSearch
from ml_benchmark.workload.mlp_objective import MLPObjective
from ml_benchmark.workload.mnist_task import MnistTask
from ml_benchmark.utils.yml_parser import YMLParser
from ml_benchmark.config import Path


@click.command()
@click.argument('hyperparameter')
@click.argument('resources')
@click.method('optimzation_method')
@click.option('--config', default=None, help='Dataset Configuration')
@click.option('--epochs', default=100, help="Number of Epochs to train per Trial")
@click.option('--result_path', default=Path.experiments_path)
def main(hyperparameter, resources, config, epochs):
    if not config:
        config = {
                "val_split_ratio": 0.2, "train_batch_size": 512, "val_batch_size": 128, "test_batch_size": 128}

    task = MnistTask()
    train_loader, val_loader, test_loader = task.create_data_loader(config)
    objective_cls = MLPObjective
    grid = YMLParser.parse(hyperparameter)
    grid["input_size"] = [task.input_size]
    grid["output_size"] = [task.output_size]
    objective_args = dict(
        epochs=epochs,
        train_loader=train_loader,
        val_loader=val_loader,
        test_loader=test_loader
        )
    optimization_method = optimization_method_cls(
        objective_cls=objective_cls, objective_args=objective_args, grid=grid, resources=resources)
    optimization_method_results = optimization_method.main()
    # save results with prerx of experiment/framework


if __name__ == "__main__":
    main()
