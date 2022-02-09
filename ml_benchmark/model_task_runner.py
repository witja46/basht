from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from torchvision.datasets import MNIST
from torch.utils.data import TensorDataset
from torchvision import transforms
import time

from ml_benchmark.mlp_objective import MLPObjective


# TODO: dataclass for results and assert if some results are missing
class ModelTaskRunner:

    def __init__(self, configuration) -> None:

        self.seed = 1337  # TODO: improve seed setting
        self.epochs = 100  # TODO: improve epoch setting
        self.objective_cls = MLPObjective
        self.configuration = configuration
        self.objective = self._set_up_objective(self.configuration)

        """
        configuration = {"hyperparameters"
        "train_batch_size"
        "test_batch_size"
        "val_batch_size"
        "val_split_ratio"}
        """

    def _set_up_objective(self, configuration):
        dataset = self.get_data()
        train_data, val_data, test_data = self.split_data(dataset, configuration["val_split_ratio"])
        train_loader = DataLoader(train_data, batch_size=configuration["train_batch_size"], shuffle=True)
        val_loader = DataLoader(val_data, batch_size=configuration["val_batch_size"], shuffle=True)
        test_loader = DataLoader(test_data, batch_size=configuration["test_batch_size"], shuffle=True)
        return dict(
            epochs=self.epochs, train_loader=train_loader,
            val_loader=val_loader, test_loader=test_loader)

    def split_data(self, dataset, val_split_ratio):
        X_train, X_val, y_train, y_val = train_test_split(
            dataset.train_data, dataset.targets, test_size=val_split_ratio, random_state=self.seed)
        train_set = TensorDataset(X_train, y_train)
        val_set = TensorDataset(X_val, y_val)
        test_set = TensorDataset(dataset.test_data, dataset.test_labels)
        return train_set, val_set, test_set

    def get_data(self):
        transform = transforms.Compose(
            [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
        mnist_data = MNIST(root="/tmp/MNIST", download=True, transform=transform)
        mnist_data = self.mnist_preprocessing(mnist_data)
        return mnist_data

    def mnist_preprocessing(self, mnist_data):
        mnist_data.data = mnist_data.data.view(-1, 28 * 28).float()
        return mnist_data

    def run(self, hyperparameters, device):
        """This function runs the training, validation and test of the objective.
        This function is supposed to work as an entrypoint for hyperparameter optimization.

        Args:
            hyperparameters ([type]): [description]
            device ([type]): [description]

        Returns:
            [type]: [description]
        """
        self.objective.set_device(device)
        self.objective.set_hyperparameters(hyperparameters)
        start_time = time.time()
        training_loss = self.train()
        validation_scores = self.validate()
        test_scores = self.test()
        results = dict(
            training_loss=training_loss,
            validation_scores=validation_scores,
            test_scores=test_scores,
            execution_time=time.time() - start_time
        )
        return results


if __name__ == "__main__":
    configuration = {
        "val_split_ratio": 0.2, "train_batch_size": 128, "val_batch_size": 64, "test_batch_size": 64}
    runner = ModelTaskRunner(configuration)
    hyperparameters = dict(
        input_size=28*28, learning_rate=1e-2, weight_decay=1e-6, hidden_layer_config=[50, 25], output_size=10)
    results = runner.run(hyperparameters=hyperparameters, device="cuda")
    print(results)  # TODO: results saving
