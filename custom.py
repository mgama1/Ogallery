from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
import datetime
import os

import cv2
from styles import *

class CustomAwesome():
    def __init(self):
        pass
    
    def concat_pixmaps(self,pixmap1, pixmap2,inv_dist):
        # Create a new QPixmap with the size of both pixmaps combined
        combined_pixmap = QPixmap(pixmap1.size().width() + pixmap2.size().width(),
                                  max(pixmap1.size().height(), pixmap2.size().height()))
        combined_pixmap.fill(Qt.transparent)  # Fill the new pixmap with transparency

        # Use QPainter to draw both pixmaps onto the new QPixmap
        painter = QPainter(combined_pixmap)
        painter.drawPixmap(0, 0, pixmap1)
        painter.drawPixmap(pixmap1.size().width()/inv_dist, 0, pixmap2)
        painter.end()

        return combined_pixmap


        
class SavingMessageBox(QMessageBox):
    def __init__(self, image_path, edited_image, *args, **kwargs):
        super(SavingMessageBox, self).__init__(*args, **kwargs)
        style = OStyle()
        self.image_path=image_path
        self.edited_image=edited_image
        self.overwrite_button = QPushButton("Overwrite")
        self.copy_button = QPushButton("Copy")
        self.overwrite_button.setFocusPolicy(Qt.NoFocus)
        self.copy_button.setFocusPolicy(Qt.NoFocus)
        self.addButton(self.overwrite_button, QMessageBox.ActionRole)
        self.addButton(self.copy_button, QMessageBox.ActionRole)
                       
        
        self.overwrite_button.clicked.connect(self.handle_overwrite)
        self.copy_button.clicked.connect(self.handle_copy)
        
        
        
        self.setWindowTitle("Save Image")
        self.setText("Do you want to overwrite the existing image or save a copy?")
        self.setStyleSheet(f"background-color: {style.color.background};color:white;")
        self.overwrite_button.setStyleSheet(f"QPushButton:hover {{background-color:{style.color.red}; }}")
        self.copy_button.setStyleSheet(f"QPushButton:hover {{background-color: {style.color.blue}; }}")

    def handle_overwrite(self):
        cv2.imwrite(self.image_path, self.edited_image)
        print(self.image_path)
    def handle_copy(self):
        mod_time = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
        cv2.imwrite(f"{os.path.splitext(self.image_path)[0]}_{mod_time}.jpg",
                    self.edited_image)
        
        
        
class InfoMessageBox(QMessageBox):
    def __init__(self,*args, **kwargs):
        super(InfoMessageBox, self).__init__(*args, **kwargs)
        style = OStyle()
        self.OK_button = QPushButton("OK")
        #self.OK_button.setFocusPolicy(Qt.NoFocus)
        self.addButton(self.OK_button, QMessageBox.ActionRole)
        self.setWindowTitle("Info")
        self.setStyleSheet(f"background-color: {style.color.background};color:white;")
        self.OK_button.setStyleSheet(f"QPushButton:hover {{background-color: {style.color.blue}; }}")

    
