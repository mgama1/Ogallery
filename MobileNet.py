from PIL import Image
import numpy as np
from skimage import transform
from tensorflow import keras
import os
import glob
import pandas as pd
from core import *
class Model:
    def __init__(self):
        self.core=Core()
        self.savedModel = keras.models.load_model("ogalleryv2.h5")
        self.file_types=['jpg','jpeg','png']
        self.classes=['ID', 'bicycle', 'boat', 'building', 'bus', 'car', 'cat', 'document', 'dog', 'forest', 'glacier', 'helicopter', 'motorcycle', 'mountain', 'plane', 'reciept', 'sea', 'street', 'train', 'truck']
        #spaces before and after words are intentional to avoid retreiving unintentional substring 
        self.classes_synonyms={"ID":"q_identity card,q_id card ",'bicycle':"q_bike", 'boat':"q_ship", 
                  'building':"q_house , q_home , q_apartment", 'bus':'q_autobus', 'car':'q_automobile ', 
                  'cat':'q_kitty ,q_kitten ', 'document':"q_docs , q_text ", 'dog':"q_puppy ,q_pupper ,q_doggo ,q_doggy ",
         'forest':"q_tree ", 'glacier':'q_ice ,q_iceberg ', 'helicopter':"q_chopper ", 'motorcycle': "q_bike ",
                  'mountain':'q_nature ', 'plane':'q_airplane ,q_aeroplane , q_aircraft', 'reciept':' q_bill ',
                  'sea':'q_beach ,q_water ','street':' ', 'train':' ', 'truck': ' '}


    def predict_batch(self,files_list):
        if not os.path.exists("./db.csv"):
            self.db = pd.DataFrame(columns=['directory', 'class',"synonyms"])
            self.db.to_csv('db.csv', index=False)

        self.db=pd.read_csv("db.csv")
        
        images_list = []
        pred_files_list=[]
        for filename in files_list:
            if filename not in self.db["directory"].values:
                pred_files_list.append(filename)
                image = Image.open(filename)
                np_image = np.array(image).astype('float32')
                np_image = transform.resize(np_image, (160, 160, 3))
                images_list.append(np_image)
        
        if len(images_list)<1:
            return 0    
        images = np.array(images_list)
        predictions = self.savedModel.predict(images)
        classes_indices = np.argmax(predictions, axis=1)
        confidences = np.max(predictions, axis=1)
        results = []
        for i, idx in enumerate(classes_indices):
            if confidences[i] > 0.70:
                results.append((pred_files_list[i], self.classes[idx]))
            else:
                results.append((pred_files_list[i], None))
        return results


    def predictAndSave(self):
        
        
        batch_results = self.predict_batch(self.core.getImagesPaths())
        
        if batch_results==0:
            return 0

        for filename, prediction in batch_results:
            if prediction is None:
                new_row = {"directory":filename,"class":None,"synonyms":None}
                self.db=pd.concat([self.db, pd.DataFrame([new_row])], ignore_index=True)
                
            else:
                new_row = {"directory":filename,"class":"q_"+prediction.lower(),"synonyms":self.classes_synonyms[prediction]}
                self.db=pd.concat([self.db, pd.DataFrame([new_row])], ignore_index=True)

        self.db.to_csv("db.csv",index=False)

