from PIL import Image
import numpy as np
from skimage import transform
from tensorflow import keras
import os
import glob
import pandas as pd
class Model:
    def __init__(self):
        self.savedModel = keras.models.load_model("ogalleryv2.h5")
        self.file_types=['jpg','jpeg','png']
        self.classes=['ID', 'bicycle', 'boat', 'building', 'bus', 'car', 'cat', 'document', 'dog', 'forest', 'glacier', 'helicopter', 'motorcycle', 'mountain', 'plane', 'reciept', 'sea', 'street', 'train', 'truck']
        #spaces before and after words are intentional to avoid retreiving unintentional substring 
        self.classes_synonyms={"ID":" identity card , id card ",'bicycle':" bike ", 'boat':" ship ", 
                  'building':" house , home , apartment ", 'bus':' autobus ', 'car':' automobile ', 
                  'cat':' kitty , kitten ', 'document':" docs , text ", 'dog':" puppy , pupper , doggo , doggy ",
         'forest':" tree ", 'glacier':' ice , iceberg ', 'helicopter':" chopper ", 'motorcycle': " bike ",
                  'mountain':' nature ', 'plane':' airplane , aeroplane , aircraft', 'reciept':' bill ',
                  'sea':' beach , water ','street':' ', 'train':' ', 'truck': ' '}


    def predict_batch(self,files_list):
        
        images_list = []
        for filename in files_list:
            if filename not in self.db["directory"].values:
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
                results.append((files_list[i], self.classes[idx]))
            else:
                results.append((files_list[i], None))
        return results


    def predictAndSave(self):
        if not os.path.exists("./db.csv"):
            self.db = pd.DataFrame(columns=['directory', 'class',"synonyms"])
            self.db.to_csv('db.csv', index=False)

        self.db=pd.read_csv("db.csv")

        username = os.getenv('USER')
        config_file_path = f'/home/{username}/.cache/OpenGallery/config.log'
        with open(config_file_path, 'r') as config_file:
                    images_directories = [line.strip() for line in config_file.readlines() if line.strip()]

        
        image_files=[]
        for images_directory in images_directories:
            for file_type in self.file_types:
                image_files+=(glob.glob(f"{images_directory}/**/*.{file_type}",
                                        recursive=True))

        
        batch_results = self.predict_batch(image_files)
        if batch_results==0:
            return 0

        for filename, prediction in batch_results:
            if prediction is None:
                new_row = {"directory":filename,"class":None,"synonyms":None}
                self.db=pd.concat([self.db, pd.DataFrame([new_row])], ignore_index=True)
                
            else:
                new_row = {"directory":filename,"class":prediction.lower(),"synonyms":self.classes_synonyms[prediction]}

                self.db=pd.concat([self.db, pd.DataFrame([new_row])], ignore_index=True)

        self.db.to_csv("db.csv",index=False)

        