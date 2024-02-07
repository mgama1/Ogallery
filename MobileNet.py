from PIL import Image
import numpy as np
from skimage import transform
from tensorflow import keras
class Model:
    def __init__(self,directory,threshold):
        self.directory= directory
        self.threshold=threshold
        self.savedModel = keras.models.load_model("ogalleryv1.h5")


    def predict(self):
        classes=['bicycle','boat','building','bus','car','forest',
                'glacier','helicopter','motorcycle', 'mountain',
                'plane','sea','street','train','truck']
        np_image = Image.open(self.directory)
        np_image = np.array(np_image).astype('float32')
        np_image = transform.resize(np_image, (160, 160, 3))
        np_image = np.expand_dims(np_image, axis=0)
        prediction=self.savedModel.predict(np_image)
        pn=np.argmax(prediction)
        conf=np.max(prediction)
        p=classes[pn]

        if conf>self.threshold:
            return p
        else:
            return None


    