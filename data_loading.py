from pathlib import Path
import glob
import torch
import os
import cv2
import pandas as pd
import pickle
import random
import numpy as np

def iterate_batches(batch_size = 128, train=True, shuffle=True):
    if train:
        dirlist = get_train_dirlist(batch_size)
    else:
        dirlist = get_valid_dirlist(batch_size)
    if shuffle:
        random.shuffle(dirlist)
    for i, filename in enumerate(dirlist):
        with open(filename, 'rb') as handle:
            minibatch = pickle.load(handle)
        yield minibatch

def get_train_dirlist(batch_size):
    dirlist = sorted(glob.glob('train_batches_regr_'+str(batch_size)+'/*.pickle'))
    return dirlist

def get_valid_dirlist(batch_size):
    dirlist = sorted(glob.glob('valid_batches'+str(batch_size)+'/*.pickle'))
    return dirlist


'''def iterate_batches(batch_size=128,train=True):
    chunksize = batch_size*100
    total_num = 200000
    total_chunk_num = int(total_num/chunksize)
    train_chunk_num = int((total_num/chunksize) * 0.7)
    if train:
        x_data_iter = pd.read_csv('out_x.csv', iterator=True)
        y_data_iter = pd.read_csv('out_labels.csv', iterator=True)
        i_max = train_chunk_num
        #print(i_max)
    else:
        x_data_iter = pd.read_csv('out_x.csv', iterator=True, skiprows=train_chunk_num*chunksize)
        y_data_iter = pd.read_csv('out_labels.csv', iterator=True, skiprows=train_chunk_num*chunksize)
        i_max = total_chunk_num-train_chunk_num
    for i in range(i_max):
        #print(i)
        x_chunk = x_data_iter.get_chunk(chunksize)
        y_chunk = y_data_iter.get_chunk(chunksize)
        x_chunk_np = x_chunk.to_numpy(dtype=np.float32)
        #print(x_chunk_np.shape)
        y_chunk_np = y_chunk.to_numpy(dtype=np.float32)
        indexes = [i for i in range(chunksize)]
        random.seed(42)
        random.shuffle(indexes)
        for n in range(0,chunksize,batch_size):
            batch_imgs = torch.empty((batch_size,1,30,30),dtype=torch.float32)
            batch_labels = torch.empty((batch_size,900),dtype=torch.float32)
            for batch_n in range(batch_size):
                batch_imgs[batch_n] = torch.Tensor(x_chunk_np[indexes[n+batch_n]].reshape((1,30,30)))
                batch_labels[batch_n] = torch.Tensor(y_chunk_np[indexes[n+batch_n]])
            yield (batch_imgs,batch_labels)
'''