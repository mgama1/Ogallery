from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt,pyqtSignal
from PyQt5.QtWidgets import *
import datetime
import os
import yaml


import cv2

basedir = os.path.dirname(__file__)

        
class SavingMessageBox(QMessageBox):
    def __init__(self, image_path, edited_image, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(os.path.join(basedir,'config/config.yaml'), 'r') as file:
            self.config_data = yaml.safe_load(file)

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
        self.setStyleSheet(f"background-color: {self.config_data['background']};color:white;")
        self.overwrite_button.setStyleSheet(f"QPushButton:hover {{background-color:{self.config_data['red']}; }}")
        self.copy_button.setStyleSheet(f"QPushButton:hover {{background-color: {self.config_data['blue']}; }}")

    def handle_overwrite(self):
        self.choice = "overwrite"


    def handle_copy(self):
        self.choice = "copy"
        
    def get_choice(self):
        return self.choice
    def getFileName(self):
        return self.file_name
        

class InfoMessageBox(QMessageBox):
    def __init__(self,*args, **kwargs):
        super(InfoMessageBox, self).__init__(*args, **kwargs)
        try:
            with open(os.path.join(basedir,'config/config.yaml'), 'r') as file:
                self.config_data = yaml.safe_load(file)
            self.OK_button = QPushButton("OK")
            #self.OK_button.setFocusPolicy(Qt.NoFocus)
            self.addButton(self.OK_button, QMessageBox.ActionRole)
            self.setWindowTitle("Info")
            self.setStyleSheet(f"background-color: {self.config_data['background']};color:white;")
            self.OK_button.setStyleSheet(f"QPushButton:hover {{background-color: {self.config_data['blue']}; }}")
        except Exception as e:
            print(f"Error: {e}")
 
  
class SaveDiscardMessageBox(QMessageBox):
    revert_signal=pyqtSignal()
    def __init__(self, image_path, edited_image, *args, **kwargs):
        super().__init__(*args, **kwargs)
        with open(os.path.join(basedir,'config/config.yaml'), 'r') as file:
            self.config_data = yaml.safe_load(file)
        self.image_path=image_path
        self.edited_image=edited_image
        self.save_button = QPushButton("Save")
        self.discard_button = QPushButton("Discard")
        self.save_button.setFocusPolicy(Qt.NoFocus)
        self.discard_button.setFocusPolicy(Qt.NoFocus)
        self.addButton(self.save_button, QMessageBox.ActionRole)
        self.addButton(self.discard_button, QMessageBox.ActionRole)
                       
        
        self.save_button.clicked.connect(self.handle_save)
        self.discard_button.clicked.connect(self.handle_discard)
        
        
        
        self.setWindowTitle("Save Image")
        self.setText("Do you want to overwrite the existing image or save a copy?")
        self.setStyleSheet(f"background-color: {self.config_data['background']};color:white;")
        self.save_button.setStyleSheet(f"QPushButton:hover {{background-color:{self.config_data['blue']}; }}")
        self.discard_button.setStyleSheet(f"QPushButton:hover {{background-color: {self.config_data['red']}; }}")
        
    def handle_save(self):
        self.choice='save'
        

    def handle_discard(self):
        self.choice='discard'
        #self.revert_signal.emit()
        
    def get_choice(self):
        return self.choice
    def getFileName(self):
        return self.file_name
 

class QPushButtonHighlight(QPushButton):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)

    
    def setIconNormal(self,icon_normal):
        self.icon_normal = icon_normal
        self.setIcon(icon_normal)
    def setIconHover(self,icon_hover):
        self.icon_hover = icon_hover
        
    def enterEvent(self, event):
        self.setIcon(self.icon_hover)

    def leaveEvent(self, event):
        self.setIcon(self.icon_normal)

class CustomDialog(QDialog):
    def __init__(self, title="Input", message="Enter text", is_password=False, *args, **kwargs):
        super(CustomDialog, self).__init__(*args, **kwargs)

        try:
            # Load colors from config file
            with open(os.path.join(basedir,'config/config.yaml'), 'r') as file:
                self.config_data = yaml.safe_load(file)

            # Set window title
            self.setWindowTitle(title)

            # Set dialog stylesheet (background and text color)
            self.setStyleSheet(f"background-color: {self.config_data['background']}; color: white;")

            # Create layout
            layout = QVBoxLayout()

            # Create label with the message
            self.label = QLabel(message)
            layout.addWidget(self.label)

            # Create input field (can be plain text or password)
            self.input = QLineEdit(self)
            if is_password:
                self.input.setEchoMode(QLineEdit.Password)  # Hide text for password input
            self.input.setStyleSheet("color: white;")  # Set text color to white
            layout.addWidget(self.input)

            # Create button
            self.ok_button = QPushButton("OK")
            self.ok_button.setStyleSheet(f"QPushButton:hover {{background-color: {self.config_data['blue']}; }}")
            self.ok_button.clicked.connect(self.accept)
            layout.addWidget(self.ok_button)

            # Set the layout
            self.setLayout(layout)

        except Exception as e:
            print(f"Error: {e}")

    def getText(self):
        """ Returns the input text if OK is clicked, else None. """
        if self.exec_() == QDialog.Accepted:
            return self.input.text()
        return None
