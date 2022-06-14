import torch
import tqdm
from sklearn.metrics import classification_report
from ml_benchmark.workload.mnist.mlp import MLP
from ml_benchmark.latency_tracker import latency_decorator
from ml_benchmark.workload.objective import Objective


class MLPObjective(Objective):

    def __init__(self, epochs, train_loader, val_loader, test_loader) -> None:
        super().__init__()
        self.train_loader = train_loader
        self.val_laoder = val_loader
        self.test_loader = test_loader
        self.hyperparameters = None
        self.epochs = epochs
        self.device = None

    def set_hyperparameters(self, hyperparameters):
        self.hyperparameters = hyperparameters

    def set_device(self, device_str=None):
        if device_str:
            self.device = torch.device(device_str)
        else:
            self.device = torch.device("cpu")

    @latency_decorator
    def train(self):
        # model setup
        self.model = MLP(**self.hyperparameters)
        self.model = self.model.to(self.device)
        # train
        epoch_losses = []
        for epoch in tqdm.tqdm(range(1, self.epochs+1)):
            batch_losses = []
            for x, y in self.train_loader:
                x = x.to(self.device)
                y = y.to(self.device)
                loss = self.model.train_step(x, y)
                batch_losses.append(loss)
            epoch_losses.append(sum(batch_losses)/len(batch_losses))
        return {"train_loss": epoch_losses}

    @latency_decorator
    def validate(self):
        self.model.eval()
        self.model = self.model.to(self.device)
        val_targets = []
        val_preds = []
        for x, y in self.val_laoder:
            x = x.to(self.device)
            y = y.to(self.device)
            predictions = self.model.test_step(x)
            targets = y.flatten().detach()
            val_targets += [targets.detach()]
            val_preds += [predictions.detach()]
        val_targets = torch.cat(val_targets).cpu().numpy()
        val_preds = torch.cat(val_preds).cpu().numpy()
        return classification_report(val_targets, val_preds, output_dict=True, zero_division=1)

    def test(self):
        self.model.eval()
        self.model = self.model.to(self.device)
        test_targets = []
        test_predictions = []
        for x, y in self.test_loader:
            x = x.to(self.device)
            y = y.to(self.device)
            predictions = self.model.test_step(x)
            targets = y.flatten().detach()
            test_targets += [targets.detach()]
            test_predictions += [predictions.detach()]
        test_targets = torch.cat(test_targets).cpu().numpy()
        test_predictions = torch.cat(test_predictions).cpu().numpy()
        return classification_report(test_targets, test_predictions, output_dict=True, zero_division=1)


if __name__ == "__main__":

    from ml_benchmark.workload.mnist.mnist_task import MnistTask
    task = MnistTask()
    epochs = 5
    configuration = {
            "val_split_ratio": 0.2, "train_batch_size": 512, "val_batch_size": 128, "test_batch_size": 128}
    train_loader, val_loader, test_loader = task.create_data_loader(configuration)
    for _ in range(5):
        objective = MLPObjective(
            epochs=epochs, train_loader=train_loader, val_loader=val_loader, test_loader=test_loader)
        objective.set_device("cpu")
        hyperparameters = dict(
                input_size=28*28, learning_rate=1e-4,
                weight_decay=1e-6,
                hidden_layer_config=[10, 10],
                output_size=10)
        objective.set_hyperparameters(hyperparameters)
        # these are the results, that can be used for the hyperparameter search
        objective.train()
        validation_scores = objective.validate()
    test_scores = objective.test()
    print(test_scores)
