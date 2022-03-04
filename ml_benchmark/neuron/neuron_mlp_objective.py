import torch
import tqdm
from sklearn.metrics import classification_report
from ml_benchmark.mlp import MLP
import torch_neuron
import uuid
import os
from ml_benchmark.neuron_mlp import NeuronMLP


class NeuronMLPObjective:

    def __init__(self, epochs, train_loader, val_loader, test_loader) -> None:
        super().__init__()
        self.train_loader = train_loader
        self.val_laoder = val_loader
        self.test_loader = test_loader
        self.hyperparameters = None
        self.epochs = epochs
        self.device = None
        self.neuron_path = os.path.dirname(os.path.abspath(__file__))
        self.obj_id = str(uuid.uuid4())

    def set_hyperparameters(self, hyperparameters):
        self.hyperparameters = hyperparameters

    def set_device(self, device_str):
        self.device = torch.device(device_str)

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
        self.model.eval()
        self.model = NeuronMLP(torch_neuron.trace(
            self.model, example_inputs=x, dynamic_batch_size=True))
        #self._save_neuron_model(self.model, x)
        return epoch_losses

    def _save_neuron_model(self, model, x, save_path=None):
        if not save_path:
            save_path = self.neuron_path
        model.eval()
        neuron_model = torch_neuron.trace(
            model, example_inputs=x, dynamic_batch_size=True)
        neuron_model.save(os.path.join(save_path, f"model_{self.obj_id}.pt"))

    def _load_neuron_model(self, load_path=None):
        if not load_path:
            load_path = self.neuron_path
        model = torch.jit.load(os.path.join(load_path, f"model_{self.obj_id}.pt"))
        return model

    def validate(self):
        model = self.model
        val_targets = []
        val_preds = []
        for x, y in self.val_laoder:
            x = x.to(self.device)
            y = y.to(self.device)
            predictions = model.test_step(x)
            targets = y.flatten().detach()
            val_targets += [targets.detach()]
            val_preds += [predictions.detach()]
        val_targets = torch.cat(val_targets).cpu().numpy()
        val_preds = torch.cat(val_preds).cpu().numpy()
        return classification_report(val_targets, val_preds, output_dict=True, zero_division=1)

    def test(self):
        model = self.model
        test_targets = []
        test_predictions = []
        for x, y in self.test_loader:
            x = x.to(self.device)
            y = y.to(self.device)
            predictions = model.test_step(x)
            targets = y.flatten().detach()
            test_targets += [targets.detach()]
            test_predictions += [predictions.detach()]
        test_targets = torch.cat(test_targets).cpu().numpy()
        test_predictions = torch.cat(test_predictions).cpu().numpy()
        return classification_report(test_targets, test_predictions, output_dict=True, zero_division=1)


if __name__ == "__main__":

    from ml_benchmark.mnist_task import MnistTask
    task = MnistTask()
    epochs = 5
    configuration = {
            "val_split_ratio": 0.2, "train_batch_size": 512, "val_batch_size": 128, "test_batch_size": 128}
    train_loader, val_loader, test_loader = task.create_data_loader(configuration)
    objective = NeuronMLPObjective(
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
