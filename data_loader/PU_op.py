import os
import pandas as pd
from scipy.io import loadmat
from sequence_aug import *

signal_size = 1024

datasetname = ["normal", "inner_race", "outer_race"]

data = []
lab = []

#working condition
WC = ["N9M7F10_01", "N15M1F10_05", "N15M7F04_01", "N15M7F10_05"]

def get_files(root, op):
    '''
    root: The location of the data set.
    ''' 
    data, lab = [], []
    
    for idx, name in enumerate(datasetname):
        data_dir = os.path.join(root, WC[op], name)

        for item in os.listdir(data_dir):
            if item.endswith('.mat'):
                item_path = os.path.join(data_dir, item)
                data_load(item_path, idx, data, lab)

    return data, lab


def data_load(item_path, label, data, lab):
    '''
    This function is mainly used to generate test data and training data.
    '''
    name = os.path.basename(item_path).split(".")[0]
    fl = loadmat(item_path)[name]
    fl = fl[0][0][2][0][6][2]  #Take out the data
    fl = fl.reshape(-1,1)

    start,end = 0, signal_size
    while end <= fl.shape[0]:
        data.append(fl[start:end])
        lab.append(label)
        start += signal_size
        end += signal_size


def data_transforms(dataset_type="train", normlize_type="-1-1"):
    transforms = {
        'train': Compose([
            Reshape(),
            Normalize(normlize_type),
            Retype()
        ]),
        'val': Compose([
            Reshape(),
            Normalize(normlize_type),
            Retype()
        ])
    }
    return transforms[dataset_type]


class PU_op(object):

    def __init__(self, data_dir, normlizetype,  op=3):
        self.data_dir = data_dir
        self.normlizetype = normlizetype
        self.op = int(op)

    def data_preprare(self, is_src=False):
        data, lab = get_files(self.data_dir, self.op)
        data_pd = pd.DataFrame({"data": data, "label": lab})
        data_pd = balance_data(data_pd)
        if is_src:   
            train_dataset = dataset(list_data=data_pd, transform=data_transforms('train', self.normlizetype))
            return train_dataset
        else:
            train_pd, val_pd = train_test_split_(data_pd, test_size=0.20, num_classes=len(datasetname))
            train_dataset = dataset(list_data=train_pd, transform=data_transforms('train', self.normlizetype))
            val_dataset = dataset(list_data=val_pd, transform=data_transforms('val', self.normlizetype))
            return train_dataset, val_dataset
        
        
if __name__ == '__main__':
    import matplotlib.pyplot as plt
    root = '../dataset/PU'
    train_dataset = PU_op(root, "-1-1").data_preprare(True)
    train_dataset.summary()
    
    midpoint = len(train_dataset) / 3
    for i in range(3):
        fig = plt.figure(figsize=(25, 12))
        for j in range(8):
            ax = fig.add_subplot(241 + j)
            ax.plot(train_dataset[int(midpoint*i+j*50)][0].reshape(-1,1))
            ax.set_xlabel('time')
            plt.legend('%d' % train_dataset[int(midpoint*i+j)][1]) 