# ml_benchmark
This repository supplies a job to benchmark hyperparameter tuning.


## Start up

### Prerequisites

* Python >= 3.7.0
* [PyTorch](https://pytorch.org/get-started/locally/)

Note: If you run your benchmark on GPU make sure to install [Cuda](https://docs.nvidia.com/cuda/cuda-installation-guide-microsoft-windows/index.html) and install the correct PyTorch Version, which fits your Cuda version.


### Install

* To install the benchmark and use it locally type, switch to the root_folder of the repository and type in `pip install -e`.


## Class Explanation

ModelTaskRunner - Runs the MNIST Task and has a run function that be modified for the hyperparameter optimization
MLPObjective - The Job that needs to be executed, if adjustments for the training are necessary, modify them here.
MLP - the model that is trained over the MNIST Task.
