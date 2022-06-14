import os
from pathlib import Path
from dataclasses import dataclass, asdict


class Path:

    file_dir = os.path.abspath(os.path.dirname(__file__))
    root_path = Path(file_dir).parent
    data_path = os.path.join(root_path, "data")
    experiments_path = os.path.join(root_path, "experiments")


@dataclass
class MnistConfig:
    val_split_ratio: float = 0.2
    train_batch_size: int = 512
    val_batch_size: int = 128
    test_batch_size: int = 128
    epochs: int = 1

    def to_dict(self):
        return asdict(self)
