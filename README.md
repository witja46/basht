# ml_benchmark
This repository supplies a job to benchmark hyperparameter tuning.


## Start up

### Prerequisites

* Ubuntu >= 16.04 (not tested on MAC OS)
* Python >= 3.7.0
* [PyTorch](https://pytorch.org/get-started/locally/)

Note: If you run your benchmark on GPU make sure to install [Cuda](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/index.html) and install the correct PyTorch Version, which fits your Cuda version.


### Install

1. Clone the repository with `git clone <url>`
2. Create a Python environment with `python -m venv .venv`.
3. Activate your environment with `source .venv/bin/activate`
4. If not already installed install [PyTorch](https://pytorch.org/get-started/locally/)
5. To install the benchmark and use it locally type, switch to the root_folder of the repository and type in `pip install -e .`


## Class Explanation

|Class|Description|
|---|---|
|ModelTaskRunner|Runs the MNIST Task and has a run function that be modified for the hyperparameter optimization|
|MLPObjective|The Job that needs to be executed, if adjustments for the training are necessary, modify them here.|
|MLP|the model that is trained over the MNIST Task.|
