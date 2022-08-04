from polyaxon import tracking
import argparse
import logging
import numpy as np
import time
# import os
# PROJECT_ROOT = os.path.abspath(os.path.join(__file__ ,"../../../.."))
# sys.path.append(PROJECT_ROOT)
# from ml_benchmark.benchmark_runner import Benchmark
# from ml_benchmark.workload.mnist.mnist_task import MnistTask


def train(times ,epoch):
    loss = 1
    for x in np.arange(1,times + 1): 
        loss = 1 - (x -1 ) / times
        time.sleep(0.01)
        msg = "Train Epoch: {} [{}/{} ({:.0f}%)]\tloss={:.4f}".format(
                epoch, x , times,
                100. * x / times, loss)
        logging.info(msg)


def test():

    test_accuracy =0.8 
    logging.info("Validation-accuracy={:.4f}\n".format(
        test_accuracy))



def main():
    
    #Polyaxon
    tracking.init()
    
    #parsing arguments 
    parser = argparse.ArgumentParser(description="MNIST Example")
    parser.add_argument("--batch-size", type=int, default=64, metavar="N",
                        help="input batch size for training (default: 64)")
    parser.add_argument("--epochs", type=int, default=10, metavar="N",
                        help="number of epochs to train (default: 10)")
    parser.add_argument("--lr", type=float, default=0.01, metavar="LR",
                        help="learning rate (default: 0.01)")
    args = parser.parse_args()
  
    #timestamps format
    logging.basicConfig(
            format="%(asctime)s %(levelname)-8s %(message)s",
            datefmt="%Y-%m-%dT%H:%M:%SZ",
            level=logging.DEBUG)

   
    #model taining and testing
    epochs = args.epochs
    batch_size = args.batch_size
    lr = args.lr
    for epoch in np.arange(1,epochs+1):
        train(batch_size,epoch)
        test() 

    # #TODO swicht to the real task 
    # task = MnistTask(config_init={"epochs": 1})
    # objective = task.create_objective()
    
    # objective.set_hyperparameters({"learning_rate": lr, "weight_decay": 0.01})
    # objective.train()
    # validation_scores = objective.validate()
    # print(validation_scores)

    #polyaxon 
    tracking.log_metrics(met1=0.8, met2= 0.9)
    tracking.log_outputs(loss=0.9,accuracy=0.6)


if __name__ == "__main__":
    main()
