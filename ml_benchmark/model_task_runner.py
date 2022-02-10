from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from torchvision.datasets import MNIST
from torch.utils.data import TensorDataset
from torchvision import transforms
import time
from rapidflow.experiments.study_result_saver import StudyResultSaver
import os
import shutil

from ml_benchmark.mlp_objective import MLPObjective


# TODO: dataclass for results and assert if some results are missing
class ModelTaskRunner:

    def __init__(self, configuration) -> None:

        self.seed = 1337  # TODO: improve seed setting
        self.epochs = configuration["epochs"]  # TODO: improve epoch setting
        self.objective_cls = MLPObjective
        self.configuration = configuration
        self.objective = self._set_up_objective(self.configuration)
        self.save_path = self._create_experiment_folder(
            experiment_file_path=os.path.abspath(os.path.dirname(__file__)), model_name="MLPObjective")
        self.saver = StudyResultSaver(experiment_path=self.save_path)

    def _create_experiment_folder(
            self, experiment_file_path, model_name, overwrite=True):
        # dict_byte_string = json.dumps(hyperparameter).encode("utf-8")
        # = hashlib.sha1(dict_byte_string).hexdigest()
        if not model_name:
            model_name = ""
        folder_name = f"exp__{model_name}"
        experiment_path = os.path.join(experiment_file_path, folder_name)
        if os.path.exists(experiment_path) and overwrite:
            shutil.rmtree(experiment_path)
        os.mkdir(experiment_path)
        return experiment_path

    def _set_up_objective(self, configuration):
        dataset = self.get_data()
        train_data, val_data, test_data = self.split_data(dataset, configuration["val_split_ratio"])
        train_loader = DataLoader(train_data, batch_size=configuration["train_batch_size"], shuffle=True)
        val_loader = DataLoader(val_data, batch_size=configuration["val_batch_size"], shuffle=True)
        test_loader = DataLoader(test_data, batch_size=configuration["test_batch_size"], shuffle=True)
        return self.objective_cls(**dict(
            epochs=self.epochs, train_loader=train_loader,
            val_loader=val_loader, test_loader=test_loader))

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

    def _save_results_and_model(self, results, model, hyperparameters):
        self.saver.save_best_model(0, model, hyperparameters, self.save_path)
        self.saver.save_study_metrics(results, "experiment_results", self.save_path)

    def set_run_function(self, run_function):
        self._run = run_function

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

        # these are the results, that can be used for the hyperparameter search
        training_loss = self.objective.train()
        validation_scores = self.objective.validate()

        # these are the results needed for the benchmark
        test_scores = self.objective.test()
        results = dict(
            test_scores=test_scores,
            execution_time=time.time() - start_time,
            training_loss=training_loss
        )
        self._save_results_and_model(results, self.objective.model, self.objective.hyperparameters)


if __name__ == "__main__":
    # TODO: run function class to make customizable for hyperparameter tuning framework, strategy pattern to inject in the task runner
    configuration = {
        "epochs": 100,
        "val_split_ratio": 0.2, "train_batch_size": 512, "val_batch_size": 128, "test_batch_size": 128}
    runner = ModelTaskRunner(configuration)

    # these are the elements that need to be optimized
    hyperparameters = dict(
        input_size=28*28, learning_rate=1e-2, weight_decay=1e-6, hidden_layer_config=[50, 25], output_size=10)
    # the device where you want to run your model (cpu, cuda)
    device = "cpu"
    runner.run(hyperparameters=hyperparameters, device=device)
    print("Done!")
