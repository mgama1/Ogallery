import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os
import seaborn as sns


class Data():
    def __init__(self,directory):
        self.directory=directory
    
    def getSubDirNames(self):
        subDirNames=os.listdir(f'{self.directory}')
        return subDirNames
    
    def getSubDirCount(self):
        subDirCount=[len(os.listdir(f'{self.directory}/{subdir}')) for subdir in self.getSubDirNames()]         
        return subDirCount        
    
    def count(self):  
        return sum(self.getSubDirCount())
        
    def summary(self):

        subDirNames=self.getSubDirNames()
        subDirCount=self.getSubDirCount()  
        return pd.DataFrame({'class':subDirNames,'count':subDirCount},
                           index=['class '+ str(i) for i in range(len(subDirNames))]).T
    def show(self,row=1,col=3):
        plt.rcParams["figure.figsize"] = (10,10)
        for subDir in self.getSubDirNames():
            plt.show()       
            for i in range(row*col):
                plt.subplot(row, col,i+1)
                fileName=os.listdir(os.path.join(self.directory,subDir))[i]
                plt.imshow(mpimg.imread(os.path.join(self.directory,subDir,fileName)))
    def countPlot(self,xSize=10,ySize=5):
        sns.set(rc={'figure.figsize':(xSize,ySize)})
        sns.barplot(x=self.getSubDirNames(),y=self.getSubDirCount())
        plt.show()

import tensorflow as tf        
class myCallback(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        if(logs.get('accuracy') >.99  and logs.get('val_accuracy')>.99):
            print("Reached 97% accuracy on training and validation")
            self.model.stop_training = True

# Instantiate class
callbacks = myCallback()
