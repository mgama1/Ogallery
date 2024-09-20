
import qtawesome as qta
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt,pyqtSignal
from PIL import Image
import os

from .Othumbnails import ThumbnailMaker

class ImageThumbnailWidget(QWidget):
    selectedSig=pyqtSignal(int)
    def __init__(self, image_path, image_files,config_data,main_widget,secure_mode=False):
        super().__init__()
        username = os.getenv('USER')
        self.cache_dir = f"/home/{username}/.cache/OpenGallery/"
        self.secure_mode=secure_mode
        self.config_data=config_data
        self.image_path = image_path
        self.image_files = image_files
        self.right_clicked=False
        self.main_widget = main_widget  # Keep a reference to MainWidget

        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()
        
        self.setStyleSheet(f"background-color: {self.config_data['background']};")
        
        
        self.label = QLabel()
        
        self.label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.label)
        self.setLayout(layout)
        
        
    def load_thumbnail(self):
        tm = ThumbnailMaker(self.cache_dir)
        thumbnail_name = tm.compute_md5(tm.add_file_scheme(self.image_path)) + ".png"
        thumbnail_path = self.cache_dir + thumbnail_name
        
        if os.path.exists(thumbnail_path):
            thumb_pil = Image.open(thumbnail_path)
            thumb_MTime = int(float(thumb_pil.info['Thumb::MTime']))
            image_MTime = int(os.path.getmtime(self.image_path))
            if image_MTime == thumb_MTime:
                pixmap = QPixmap(thumbnail_path)
            else:
                tm.create_thumbnail(self.image_path)
                pixmap = QPixmap(thumbnail_path)
        else:
            tm.create_thumbnail(self.image_path)
            pixmap = QPixmap(thumbnail_path)
        
        pixmap = pixmap.scaledToWidth(200)  
        self.label.setPixmap(pixmap)
        
    
    def enterEvent(self, event):
        if not self.right_clicked:
            self.setStyleSheet(f"background-color: {self.config_data['hover_default']};")

    def leaveEvent(self, event):
        if not self.right_clicked:
            self.setStyleSheet(f"background-color: {self.config_data['background']};")
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setStyleSheet(f"background-color: {self.config_data['royal_blue']};")
            
            self.main_widget.openViewer(self.image_path,self.secure_mode)
    
        if event.button() == Qt.RightButton:
            
            if hasattr(self,'right_clicked'):
                self.right_clicked= not self.right_clicked
            else:
                self.right_clicked = True
            colors=[self.config_data['background'],'#3f5b63']
            self.setStyleSheet(f"background-color: {colors[self.right_clicked]};")
            self.selectedSig.emit(self.image_files.index(self.image_path))
    

    