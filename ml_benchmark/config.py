import os


class Path:

    root = os.path.abspath(os.path.dirname(__file__))
    data = os.path.join(root, "data")
