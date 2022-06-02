import os
from pathlib import Path


class Path:

    file_dir = os.path.abspath(os.path.dirname(__file__))
    root_path = Path(file_dir).parent
    data_path = os.path.join(root_path, "data")
    experiments_path = os.path.join(root_path, "experiments")
