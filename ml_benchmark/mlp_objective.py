
import torch
import tqdm
from sklearn.metrics import classification_report
import time
from ml_benchmark.models.mlp import MLP


# TODO: validation loss, dataclass for results and assert if some results are missing
class MLPObjective:

    def __init__(self, epochs, hyperparameters, train_loader, val_loader, test_loader, device) -> None:
        super().__init__()
        self.train_loader = train_loader
        self.val_laoder = val_loader
        self.test_loader = test_loader
        self.hyperparameters = hyperparameters
        self.epochs = epochs
        self.device = device

    def train(self):
        # for optuna usage
        # hyperparameters = dict(
        #     input_size=20,
        #     learning_rate=trial.suggest_float("learning_rate", 1e-3, 0.1, log=True),
        #     weight_decay=trial.suggest_float("weight_decay", 1e-6, 1e-4, log=True),
        #     hidden_layer_config=[
        #         trial.suggest_int(f"layer_{idx}_size", 10, 100)
        #         for idx in range(trial.suggest_int("n_layers", 1, 3))],
        #     output_size=1
        # )

        # model setup
        self.model = MLP(**self.hyperparameters)
        self.model.to(self.device)
        # train
        epoch_losses = []
        for epoch in tqdm.tqdm(range(1, self.epochs+1)):
            batch_losses = []
            for x, y in self.train_loader:
                x = x.to(self.device)
                y = y.to(self.device)
                self.model.train()
                loss = self.model.train_step(x, y)
                batch_losses.append(loss)
            epoch_losses.append(sum(batch_losses)/len(batch_losses))
        return epoch_losses

    def validate(self):
        self.model.eval()
        self.model.to(self.device)
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
        return classification_report(val_targets, val_preds, output_dict=True)

    def test(self):
        self.model.eval()
        self.model.to(self.device)
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
        return classification_report(test_targets, test_predictions, output_dict=True)

    def run_objective(self):
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
