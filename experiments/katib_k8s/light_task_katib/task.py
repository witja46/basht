import argparse
import logging
from time import sleep
from ml_benchmark.decorators import latency_decorator

@latency_decorator
def train(time_sec):
    
 
    for x in range(time_sec):
        sleep(1)
        msg = f"Train time {x}/{time_sec}"
        logging.info(msg)

@latency_decorator
def validate(time_sec):


    for x in range(time_sec):
        sleep(1)
        msg = f"Validate time {x}/{time_sec}"
        logging.info(msg)
    test_accuracy =0.7 
    logging.info("precision={:.4f}\n".format(
        test_accuracy))
   



def main():
    
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
    
    train(30)
    validate(10) 




if __name__ == "__main__":
    main()
