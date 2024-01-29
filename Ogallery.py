import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt,pyqtSignal
from PyQt5.QtWidgets import QPushButton,QSizePolicy
from PyQt5.QtGui import QColor,QFont
from PyQt5.QtGui import QImage
import cv2
import numpy as np
import time
from __future__ import print_function
import pandas as pd
from numpy.linalg import norm
import argparse
import rembg
import imagehash
from PIL import Image
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = '/path/to/your/qt/plugins'
from PyQt5.QtCore import pyqtSlot
class PathInputWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
    def init_ui(self):
        self.setWindowTitle('OGallery')
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout(self)
        horizontal_layout = QHBoxLayout()
        self.setStyleSheet("background-color: #222324;")

        
        self.logo_label = QLabel(self)
        
        pixmap = QPixmap('logo.jpg')#.scaled(300, 300)
        self.logo_label.setPixmap(pixmap)
        #self.logo_label.setScaledContents(True)
        self.logo_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.logo_label)
        
        
        self.query = QLineEdit(self)
        self.query.setFixedHeight(33)
        horizontal_layout.addWidget(self.query)
        search_button = QPushButton('➤', self)
        font = QFont()
        font.setPointSize(16)  # Change 16 to the desired font size
        search_button.setFont(font)
        search_button.clicked.connect(self.open_image_viewer)
        search_button.setFixedSize(36, 36)  # Adjust the width and height as needed
        horizontal_layout.addWidget(search_button)
        layout.addLayout(horizontal_layout)
        layout.addStretch(1)
        button_style = "QPushButton { background-color: #212121; color: white; border: 2px solid #2e2e2e;border-radius: 18px;padding: 5px;}"
        search_button.setStyleSheet(button_style) 
        line_style = (
            "QLineEdit {"
            "background-color: #212121; "
            "color: white; "
            "border-radius: 15px; "
            "padding: 5px; "
            "border: 2px solid #2e2e2e;"
            "}"
        )
        
        self.query.setStyleSheet(line_style)
        
        self.show()

    def open_image_viewer(self):
        self.selectImages()

        self.viewer = ImageViewer(self.result, self)
        self.viewer.finishedSignal.connect(self.showMainWidget)
        self.viewer.show()
        self.hide()
        

    def showMainWidget(self):
    # Show the main widget when the ImageViewer is closed
        self.show()
    def selectImages(self):
        self.queryText=self.query.text()
        self.queryText=self.suggestClasses(self.queryText,.8)
        if self.queryText=='':
            self.show_error_message(
                "there are no images found (⌣̩̩́_⌣̩̩̀)")
            
            
        db=pd.read_csv("log.csv")
        self.result=db[db["class"]==self.queryText]["directory"].to_list()
                
    
    
    def suggestClasses(self,query,threshold=.7):
        '''
        finds the cosine similarity between existing classes and 
        the search query and returns the classes above certain threshold
        inputs: str query
        outputs: list of suggested classes 
        '''
        classes=['plane','car','cat','dog','food','sea','documents']
        query=query.lower()
        cosine_prev=0
        suggested=''
        for classi in classes:
            v1=dict.fromkeys(set(query+classi),0)
            v2=dict.fromkeys(set(query+classi),0)
            for e in query:
                    v1[e]+=1
            for e in classi:
                    v2[e]+=1


            A = np.array(list(v1.values()))
            B = np.array(list(v2.values()))


            # compute cosine similarity
            cosine = np.sum(A*B, axis=0)/(norm(A, axis=0)*norm(B, axis=0))
            if (cosine >cosine_prev) and (cosine >threshold):
                    suggested= classi
                    cosine_prev=cosine
        return suggested
    
    
    def keyPressEvent(self, event):
        if (event.key() == Qt.Key_Return) or (event.key() == Qt.Key_Enter):
            self.open_image_viewer()
            
    def show_error_message(self,msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(msg)
        msg_box.setWindowTitle('Warning')
        msg_box.exec_()

class ImageViewer(QWidget):
    finishedSignal = pyqtSignal()
    def __init__(self, result, path_input_widget):
        super().__init__()

        self.file_list = []
        self.current_index = 0
        self.primary_screen = QDesktopWidget().screenGeometry()
        self.screen_width = self.primary_screen.width()
        self.screen_height = self.primary_screen.height()
        self.result = result
        self.path_input_widget = path_input_widget  # Store reference to the main widget
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Image Viewer')
        self.setGeometry(100, 100, 800, 600)
        self.setStyleSheet("background-color: #222324;")
        
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.keylist = []
        self.file_list = []
        self.current_index = 0
        self.setMouseTracking(True)
        self.load_images()

        # Main layout using QVBoxLayout
        layout = QVBoxLayout(self)
        button_layout = QHBoxLayout(self)
        Hlayout=QHBoxLayout(self)

        self.leftBrowse = QPushButton('〈', self)
        self.rightBrowse = QPushButton('〉', self)
        
        Hlayout.addWidget(self.leftBrowse)
        Hlayout.addWidget(self.image_label)
        Hlayout.addWidget(self.rightBrowse)

        

        # Create buttons and add to the grid layout
        self.process_button = QPushButton('Invert', self)
        self.gray_button = QPushButton('Gray scale', self)
        self.gaussianBlur_button = QPushButton('Smooth', self)
        self.rotate_button = QPushButton('↶', self)
        self.set_exposure_button = QPushButton('Exposure', self)
        self.save_button = QPushButton('💾', self)
        self.back_button = QPushButton('↩', self)
        self.back_button.setGeometry(10, 0, 60, 40) 


        button_layout.addWidget(self.process_button)
        button_layout.addWidget(self.gray_button)
        button_layout.addWidget(self.gaussianBlur_button)
        button_layout.addWidget(self.rotate_button)
        button_layout.addWidget(self.set_exposure_button)
        button_layout.addWidget(self.save_button)
        
        
        layout.addLayout(Hlayout)
        layout.addLayout(button_layout)

        

        self.setLayout(layout)

        # Connect button signals to their respective functions
        self.process_button.clicked.connect(self.process_image)
        self.gray_button.clicked.connect(self.BGR2GRAY)
        self.gaussianBlur_button.clicked.connect(self.gaussianBlur)
        self.rotate_button.clicked.connect(self.rotateCCW)
        self.set_exposure_button.clicked.connect(self.toggle_exposure_slider)
        self.save_button.clicked.connect(self.save_image)
        self.back_button.clicked.connect(self.goHome)
        self.leftBrowse.clicked.connect(self.next_image)
        self.rightBrowse.clicked.connect(self.previous_image)
        
        self.rightBrowse.enterEvent = self.on_enter_event
        self.rightBrowse.leaveEvent = self.on_leave_event
        self.leftBrowse.enterEvent = self.on_enter_event
        self.leftBrowse.leaveEvent = self.on_leave_event
      # Set background color for all buttons
        mediumFont = QFont()
        mediumFont.setPointSize(16)
        bigFont = QFont()
        bigFont.setPointSize(20)
        button_style = "QPushButton { background-color: #212121; color: white; }"
        
        self.process_button.setStyleSheet(button_style)
        self.gray_button.setStyleSheet(button_style)
        self.gaussianBlur_button.setStyleSheet(button_style)
        self.rotate_button.setStyleSheet(button_style)
        self.save_button.setStyleSheet(button_style)
        self.set_exposure_button.setStyleSheet(button_style)
        
        self.back_button.setStyleSheet("background-color: rgba(22, 22, 22, .5); border:none; color: white;")
        self.back_button.setFont(mediumFont)

        self.leftBrowse.setFixedSize(60, self.height())
        self.leftBrowse.setStyleSheet("background-color: rgba(22, 22, 22, .5); border: none ;color: white;")
        self.leftBrowse.setFont(bigFont)
        
        self.rightBrowse.setFixedSize(60, self.height())
        self.rightBrowse.setStyleSheet("background-color: rgba(22, 22, 22, .5); color: white; border: none ;")
        self.rightBrowse.setFont(bigFont)
        self.set_transparency(0)
        
        
        
        
        #-----------------------------------------------------
        self.image_label.setFocusPolicy(Qt.StrongFocus)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        self.load_images()

        self.show_image()

        self.show()

    def load_images(self):
        self.file_list = self.result
        
    def show_image(self):
       
        if self.file_list:
            image_path = self.file_list[self.current_index]
            pixmap = QPixmap(image_path)
            img = cv2.imread(image_path)
            self.image_label.setPixmap(pixmap.scaled(round(self.screen_width*.8),
                                                     round(self.screen_height*.8),
                                                     Qt.KeepAspectRatio,
                                                     Qt.SmoothTransformation))
            self.setWindowTitle(f'Image Viewer - {os.path.basename(image_path)}')

    def keyPressEvent(self, event):
        
        #Navigating images in the directory
        if event.key() == Qt.Key_Right:
            self.next_image()
        elif event.key() == Qt.Key_Left:
            self.previous_image()
    
        if event.key() == Qt.Key_Backspace:
            self.goHome()

        #saving edited images using key event ctrl&s
        if event.key()== Qt.Key_Control:
            self.keylist.append(Qt.Key_Control)
            print(self.keylist)#to be deleted later
            
        if event.key()==Qt.Key_S :
            self.keylist.append(Qt.Key_S)
            print(self.keylist)#to be deleted later
        
        if len(self.keylist)==2:
            if (self.keylist[0]*self.keylist[1])==Qt.Key_Control*Qt.Key_S:
                self.save_image()
         
        
    
    def keyReleaseEvent(self, event):
        time.sleep(.2)
        self.keylist=[] #clear keylist
        
    def next_image(self):
        self.current_index = (self.current_index + 1) % len(self.file_list)
        self.show_image()

    def previous_image(self):
        self.current_index = (self.current_index - 1) % len(self.file_list)
        self.show_image()
        
    
    def set_transparency(self, alpha):
        self.rightBrowse.setStyleSheet(f"background-color: rgba(22,22,22,{alpha});border: none;color: rgba(255,255,255,{alpha});")
        self.leftBrowse.setStyleSheet(f"background-color: rgba(22,22,22,{alpha});border: none;color: rgba(255,255,255,{alpha});")

    def on_enter_event(self, event):
        # Set transparency when mouse enters
        self.set_transparency(.5)

    def on_leave_event(self, event):
        # Set transparency back to normal when mouse leaves
        self.set_transparency(0)
        
    def process_image(self):
            if hasattr(self, 'edited_image'):
                img=self.edited_image
            else :
                image_path = self.file_list[self.current_index]
                img = cv2.imread(image_path)

            inverted_img = 255 - img
            self.edited_image=inverted_img
            pixmap = self.convert_cv_image_to_qpixmap(inverted_img)
            self.image_label.setPixmap(pixmap.scaled(round(self.screen_width*.8),
                                                     round(self.screen_height*.8),
                                                     Qt.KeepAspectRatio,
                                                     Qt.SmoothTransformation))
    def  BGR2GRAY(self):
        if hasattr(self, 'edited_image'):
            img=self.edited_image
        else :
            image_path = self.file_list[self.current_index]
            img = cv2.imread(image_path)
        
        gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        gray_3C=cv2.merge([gray,gray,gray])
        
        self.edited_image=gray_3C
        pixmap = self.convert_cv_image_to_qpixmap(gray_3C)
        self.image_label.setPixmap(pixmap.scaled(round(self.screen_width*.8),
                                                 round(self.screen_height*.8),
                                                 Qt.KeepAspectRatio,
                                                 Qt.SmoothTransformation))
    
    def gaussianBlur(self):
        if hasattr(self, 'edited_image'):
            img=self.edited_image
        else :
            image_path = self.file_list[self.current_index]
            img = cv2.imread(image_path)
        Blurred_img=cv2.GaussianBlur(img,ksize=(3,3),sigmaX=1)
        self.edited_image=Blurred_img
        pixmap = self.convert_cv_image_to_qpixmap(Blurred_img)
        self.image_label.setPixmap(pixmap.scaled(round(self.screen_width*.8),
                                                 round(self.screen_height*.8),
                                                 Qt.KeepAspectRatio, 
                                                 Qt.SmoothTransformation))
    
    def rotateCCW(self):
        if hasattr(self, 'edited_image'):
            img=self.edited_image
        else :
            image_path = self.file_list[self.current_index]
            img = cv2.imread(image_path)
        rotatedImg=cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        self.edited_image=rotatedImg
        pixmap = self.convert_cv_image_to_qpixmap(rotatedImg)
        self.image_label.setPixmap(pixmap.scaled(round(self.screen_width*.8),
                                                 round(self.screen_height*.8),
                                                 Qt.KeepAspectRatio, 
                                                 Qt.SmoothTransformation))
    

    def toggle_exposure_slider(self):
    # Toggle the visibility of the slider when the button is pressed
        self.exposure_slider.setVisible(not self.exposure_slider.isVisible())

    def update_exposure(self, gamma1e2):

        image_path = self.file_list[self.current_index]
        img = cv2.imread(image_path)
        gamma=gamma1e2/100
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
        exposureImg= cv2.LUT(img, table)
        self.edited_image=exposureImg
        pixmap = self.convert_cv_image_to_qpixmap(exposureImg)
        self.image_label.setPixmap(pixmap.scaled(round(self.screen_width*.8),
                                                 round(self.screen_height*.8),
                                                 Qt.KeepAspectRatio,
                                                 Qt.SmoothTransformation))
    
    def convert_cv_image_to_qpixmap(self, cv_image):
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            height, width, channel = cv_image.shape
            bytes_per_line = 3 * width
            q_image = QImage(cv_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            return QPixmap.fromImage(q_image)


            return QPixmap.fromImage(image)
        
    def save_image(self):
        if hasattr(self, 'edited_image'):
            cv2.imwrite(f"{self.file_list[self.current_index]} Copy",self.edited_image)  
            self.show_success_message()
            delattr(self,'edited_image')
        else:
            self.show_error_message("no changes made to save")
    def show_success_message(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("Saved successfully!")
        msg_box.setWindowTitle("Success")
        msg_box.exec_()
        
    
    def show_error_message(self,msg):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(msg)
        msg_box.setWindowTitle('Warning')
        msg_box.exec_()
    
    def goHome(self):  
         # Hide the current widget (ImageViewer)
        self.hide()

        # Close the current widget (ImageViewer)
        self.close()
        
    def closeEvent(self, event):
        # Override the closeEvent method to handle the window close event
        self.finishedSignal.emit()
        event.accept()
        #self.closeApp()
        
   # @pyqtSlot()
    #def closeApp(self):
        #print("Exiting application")
      #  print(self.file_list)
      #  app.quit()
if __name__ == '__main__':
    app = QApplication([])

    
    
    
    
    
    

    
    
    
    
    path_input_widget = PathInputWidget()

    app.exec_()
