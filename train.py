#import architecture
from architecture import ResNet18
from architecture import BasicBlock
#from test import metrics_and_loss
import torch
import torch.nn as nn
import torch.nn.functional as F  # this includes tensor functions that we can use in backwards pass
import torchvision
import torchvision.datasets as datasets
import torch.optim as optim
import numpy as np
import matplotlib
matplotlib.use('WebAgg',force=True)
import matplotlib.pyplot as plt
import pickle
from data_loading import iterate_batches

import pandas as pd
from pathlib import Path
import random
from tqdm import tqdm




class EarlyStopper:
    def __init__(self,model, patience=1, min_delta=0):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.min_validation_loss = np.inf
        self.best_model = model

    def early_stop(self, validation_loss, model):
        if validation_loss < self.min_validation_loss:
            self.min_validation_loss = validation_loss
            self.counter = 0
            self.best_model = model
        elif validation_loss > (self.min_validation_loss + self.min_delta):
            self.counter += 1
            if self.counter >= self.patience:
                return True
        return False
    def get_best_model(self):
        return self.best_model

def main():
    use_cuda = torch.cuda.is_available()
    #for debugging it is sometimes useful to set the device to cpu as it usually gives more meaningful error messages
    #device = torch.device("cpu")
    device = torch.device("cuda" if use_cuda else "cpu")
    print("Training on device:"+str(device))

    loss_function = nn.MSELoss() 
    k_folds = 4
    n_epochs = 150
    batch_size=128
    weight_decay=0.0
    #split = int((dataframe.shape[0]/batch_size)*0.8)
        

    history = {}
    

    thenet = ResNet18(img_channels=1, num_layers=18, block=BasicBlock, num_classes=2)
    
    thenet.to(device)
    optimizer1 = optim.Adam( thenet.parameters(), weight_decay=weight_decay,lr=0.01 )

    val_auc_score = []
    val_rec = []
    train_acc = []
    val_acc = []
    train_loss = []
    val_loss = []
    early_stopper = EarlyStopper(thenet,patience=10, min_delta=0.01)

    for epoch in range(n_epochs): # number of times to loop over the dataset
        
        thenet.train()
        total_loss = 0 
        total_correct = 0 
        total_examples = 0 
        n_mini_batches = 0
        #trainloader = dataIterator(dataframe,batch_size)
        
        #trainloader reads the batches from storage and provides them in the format (images, labels)
        trainloader = iterate_batches()
        for i, mini_batch in tqdm(enumerate(trainloader, 0), unit="batch", total=1561):
        #for i, mini_batch in enumerate( trainloader, 0):
            images, labels = mini_batch
            #images = torch.reshape(images,(128,1,15,15))
            #print(i)
            images, labels = images.to(device), labels.to(device)
            # zero the parameter gradients
            # all the parameters that are being updated are in the optimizer, 
            # so if we zero the gradients of all the tensors in the optimizer, 
            # that is the safest way to zero all the gradients
            optimizer1.zero_grad()
            #print(images)
            outputs = thenet(images) # this is the forward pass

            loss = loss_function ( outputs, labels )

            loss.backward() # does the backward pass and computes all gradients

            optimizer1.step() # does one optimisation step

            n_mini_batches += 1 # keep track of number of minibatches, and collect the loss for each minibatch
            total_loss += loss.item() # loss is a zero-order tensor
            # so that to extract its value, we use .item(), as we cannot index as there are no dimensions

            # keep track of number of examples, and collect number correct in each minibatch
            # total_correct += sum( ( outputs > 0.5 ) == ( labels > 0.5 ) ).item()
            # total_examples += len( labels )

        # calculate statistics for each epoch and print them. 
        # epoch_training_accuracy = total_correct / total_examples
        epoch_training_loss = total_loss / n_mini_batches

        # epoch_val_accuracy, epoch_val_auc_score , epoch_val_recall, epoch_val_loss = metrics_and_loss( thenet, loss_function,device)

        print('Epoch %d loss: %.3f'
                %(epoch+1, epoch_training_loss))
        
        train_loss.append( epoch_training_loss )
        #train_acc.append( epoch_training_accuracy )
        #val_loss.append( epoch_val_loss )
        #val_acc.append( epoch_val_accuracy )
        #val_rec.append( epoch_val_recall)
        #val_auc_score.append(epoch_val_auc_score)
        #making sure that we dont diverge because of overfitting
        if early_stopper.early_stop(epoch_training_loss, thenet):             
            break

    history['train_loss'] = train_loss
    #history['train_acc'] = train_acc
    #history['val_loss'] = val_loss
    #history['val_acc'] = val_acc
    #history['val_rec'] = val_rec
    #history['val_auc_score'] = val_auc_score
    cwd = Path.cwd()
    #saving the model
    
    torch.save(early_stopper.get_best_model().state_dict(), f"{cwd}/model/TestModel.pickle")
    
    plt.plot( history['train_loss'], label='train_loss')
    #plt.plot( history['val_acc'], label='val_acc')
    #plt.plot( history['val_rec_' + str(fold)], label='val_rec_'+ str(fold))
    #plt.plot( history['val_auc_score'], label='val_auc_score')
    plt.legend()
    plt.show()
    # for fold in range(k_folds):
    #     plt.plot( history['train_acc_' + str(fold)], label='train_acc_'+ str(fold))
    #     plt.plot( history['val_acc_' + str(fold)], label='val_acc_'+ str(fold))
    #     #plt.plot( history['val_rec_' + str(fold)], label='val_rec_'+ str(fold))
    #     plt.plot( history['val_auc_score_' + str(fold)], label='val_auc_score_'+ str(fold))
    # plt.legend()
    # plt.show()

if __name__=='__main__':
    main()