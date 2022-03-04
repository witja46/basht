from torch.utils.data import DataLoader
from sklearn.model_selection import train_test_split
from torchvision.datasets import MNIST
from torch.utils.data import Dataset
from torch.utils.data import TensorDataset
from torchvision import transforms
from ml_benchmark.config import Path
import os


# TODO: dataclass for results and assert if some results are missing
class MnistTask:

    def __init__(self) -> None:

        self.seed = 1337  # TODO: improve seed setting
        self.input_size = 28*28
        self.output_size = 10

    def create_data_loader(self, configuration):
        dataset = self._get_data()
        train_data, val_data, test_data = self._split_data(dataset, configuration["val_split_ratio"])
        train_loader = DataLoader(train_data, batch_size=configuration["train_batch_size"], shuffle=True)
        val_loader = DataLoader(val_data, batch_size=configuration["val_batch_size"], shuffle=True)
        test_loader = DataLoader(test_data, batch_size=configuration["test_batch_size"], shuffle=True)
        return train_loader, val_loader, test_loader

    def _split_data(self, dataset, val_split_ratio):
        X_train, X_val, y_train, y_val = train_test_split(
            dataset.train_data, dataset.targets, test_size=val_split_ratio, random_state=self.seed)
        train_set = TensorDataset(X_train, y_train)
        val_set = TensorDataset(X_val, y_val)
        test_set = TensorDataset(dataset.test_data, dataset.test_labels)
        return train_set, val_set, test_set

    def _get_data(self):
        transform = transforms.Compose(
            [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])
        mnist_data = MNIST(root=os.path.join(Path.data_path, "MNIST"), download=True, transform=transform)
        mnist_data = self.mnist_preprocessing(mnist_data)
        return mnist_data

    def mnist_preprocessing(self, mnist_data):
        mnist_data.data = mnist_data.data.view(-1, 28 * 28).float()
        return mnist_data


class MNISTDataset(Dataset):
    def __init__(self) -> None:
        super().__init__()
        mnist_path = os.path.join(Path.data_path, "MNIST")

    def __getitem__(self, index):
        return super().__getitem__(index)

    def __len__(self):
        return 1
