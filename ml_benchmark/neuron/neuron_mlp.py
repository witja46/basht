import torch.nn as nn
import torch


class NeuronMLP:

    def __init__(self, model=None, optimizer=None):
        if model:
            self.model = model
        self.criterion = nn.CrossEntropyLoss()
        self.softmax = nn.Softmax(dim=1)

    def loss_function(self, x, target):
        return self.criterion(x, target)

    def predict(self, logits):
        probabilities = self.softmax(logits)
        predictions = probabilities.to(dtype=torch.int16).argmax(dim=1)
        return predictions

    def test_step(self, x):
        logits = self.model(x)
        predictions = self.predict(logits)
        return predictions
