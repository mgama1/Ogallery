import os
import glob
class Core():
    def __init__(self):
        self.file_types=['jpg','jpeg','png','gif']
    
    def getImagesPaths(self):
        username = os.getenv('USER')
        config_file_path = f'/home/{username}/.cache/OpenGallery/config.log'

        with open(config_file_path, 'r') as config_file:
            images_directories = [line.strip() for line in config_file.readlines() if line.strip()]
        
        image_files=[]
        for images_directory in images_directories:
            for file_type in self.file_types:
                image_files+=(glob.glob(f"{images_directory}/**/*.{file_type}",
                                        recursive=True))
        image_files.sort(key=lambda x: os.path.getmtime(x),reverse=True)
        
        return image_files