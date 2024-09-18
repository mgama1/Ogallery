import os
import glob
import fnmatch

class ImagesModel():
    def __init__(self):
        self.file_types=['jpg','jpeg','png','gif']
        username = os.getenv('USER')
        config_file_path = f'/home/{username}/.cache/OpenGallery/config.log'

        with open(config_file_path, 'r') as config_file:
            self.images_directories = [line.strip() for line in config_file.readlines() if line.strip()]
    
    def getImagesPaths(self):
        
        
        image_files=[]
        for images_directory in self.images_directories:
            for file_type in self.file_types:
                image_files+=(glob.glob(f"{images_directory}/**/*.{file_type}",
                                        recursive=True))
        image_files.sort(key=lambda x: os.path.getmtime(x),reverse=True)
        
        return image_files
    
    def get_secure_files(self):
        
        secure_files=[]
        for images_directory in self.images_directories:
                secure_files+=self.find_secure_files(images_directory)
        return secure_files
    
    def find_secure_files(self,parent_dir):
        matches = []
        for root, dirnames, filenames in os.walk(parent_dir):
            for filename in fnmatch.filter(filenames, '*.ogcrypt'):
                matches.append(os.path.join(root, filename))
        return matches
