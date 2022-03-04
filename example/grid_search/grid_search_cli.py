import click
from ml_benchmark.grid_search import GridSearch
from ml_benchmark.mlp_objective import MLPObjective
from ml_benchmark.mnist_task import MnistTask
from ml_benchmark.yml_parser import YMLParser


@click.command()
@click.argument('hyperparameter')
@click.option('--config', default=None, help='Dataset Configuration')
@click.option('--epochs', default=5, help="Number of Epochs to train per Trial")
@click.option('--neuron', default=False, help="defines whether to use neuron engine")
@click.option("--device", default="cpu", help="Define on which device grid search shall be executed")
@click.option("--num-processes", default=None, help="Define the Number of Processes")
def main(hyperparameter, config, epochs, neuron, device, num_processes):
    if not config:
        config = {
                "val_split_ratio": 0.2, "train_batch_size": 512, "val_batch_size": 128, "test_batch_size": 128}

    task = MnistTask()
    train_loader, val_loader, test_loader = task.create_data_loader(config)
    if not neuron:
        objective_cls = MLPObjective
    else:
        from ml_benchmark.neuron.neuron_mlp_objective import NeuronMLPObjective
        objective_cls = NeuronMLPObjective
    grid = YMLParser.parse(hyperparameter)
    grid["input_size"] = [task.input_size]
    grid["output_size"] = [task.output_size]
    objective_args = dict(
        epochs=epochs,
        train_loader=train_loader,
        val_loader=val_loader,
        test_loader=test_loader
        )
    grid_search = GridSearch(
        objective_cls=objective_cls, objective_args=objective_args, grid=grid, device=device,
        num_processes=num_processes)
    grid_search.main()


if __name__ == "__main__":
    main()
