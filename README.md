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
4. Upgrade pip with `pip install pip --upgrade`
5. If not already installed install [PyTorch](https://pytorch.org/get-started/locally/)
6. To install the benchmark and use it locally type, switch to the root_folder of the repository and type in `pip install -e .`


## Class Explanation

|Class|Description|
|---|---|
|MNISTTask|Use it to get the Data for the Model. Please do not change its configuration|
|MLPObjective|The Job that needs to be executed. Adjustments should not be neccessary.|
|MLP|The model that is trained over the MNIST Task.|


# Benchmark Methodolegy

Each implementation uses a common **experiment-docker-container** that represents the full lifecycle of a benchmarking experiment, see the lifecycle figure.

![lifecycle](docs/lifecycle.jpg).

The docker container stub is located [here](todo).

## Lifecycle
The Lifecycle consists of 7 steps, that we describe in detail in the following:

### Deploy
The first step in each bechmark is the provisioning/deployment of the resouces used in the benchmark, e.g,. in the case of kubernetes it referes to the steps nassary to deploy all pods and services in kubernetes.
### Setup
The Setup refers to all nassesary steps the hyperparameter optimiation client needs to perfrom in order to start the seach process. This includes the loading of the framework, configuring the framework, seach space etc. 
The setup step will also initiate the distributed trails, thus, the setup step ends when the first trail is submitted to the underling cloud platfrom.
### Trail
A trail is a single training loop for a specific hyperparameter set. Within each trail, traingsdata is loaded, the model is trained and validated. 
### Result Collection
Result collection is the process of collecting the results of all distributed trails to find the best perfoming hyperparameter for the provided model. Depending on the framework, this step might be a continues process that end once all trails are compleat or a process that is triggered after the framework under test observed the compleation of all trails. 
However, for this benchmark we allways measure the result collection as the time between the last compleated trail and the identification of the best performing hyperparameter set.

### Test


### Metric Collection
Metrics Collection is a nessary step of the benchmarking process and might require the collection of logs and other measurmentes from all deployed resouces, thus it can only happen after the test step, however, the duration of this step is not critical for the comparison of benchmarking results.

### Un-Deploy
This step records the time it takes until all resocues that were deployed in the **Deploy** step are removed, or reset into a state so that the same benchmark can run again, starting with the Deploy step.