classesNames=['bicycle','boat','building','bus','car','forest',
             'glacier','helicopter','motorcycle', 'mountain',
             'plane','sea','street','train','truck']

import os
import time
import datetime
import subprocess

import qtawesome as qta
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap,QColor,QFont,QImage,QIcon
from PyQt5.QtCore import Qt,pyqtSignal,QPoint,QSize,QTimer
import numpy as np
import pandas as pd
import cv2
from PIL import Image
#import imagehash
from Levenshtein import distance as lev_distance
from __future__ import print_function
import argparse
import rembg


os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = '/path/to/your/qt/plugins'
from PyQt5.QtCore import pyqtSlot
class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
    def init_ui(self):
        self.setWindowTitle('OGallery')
        self.setGeometry(300, 100, 800, 650)
        
       
        #buttons instantiation
        self.query = QLineEdit(self)
        self.search_button = QPushButton('➤', self)
        self.info_button=QPushButton('ⓘ',self)
        self.settings_button=QPushButton('⚙',self)
        
        #Autocomplete using QCompleter
        completer = QCompleter(classesNames, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.query.setCompleter(completer)
        
        #logo QLabel instantiation and settings
        self.logo_label = QLabel(self)
        pixmap = QPixmap('logo.jpg')
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        
        #layout structure 
        layout = QVBoxLayout(self)
        horizontal_layout = QHBoxLayout()
        header_layout=QHBoxLayout()
        
        header_layout.addWidget(self.settings_button)
        header_layout.addStretch(1)
        header_layout.addWidget(self.info_button)
                
        layout.addLayout(header_layout)
        layout.addWidget(self.logo_label)
                
        horizontal_layout.addWidget(self.query)
        horizontal_layout.addWidget(self.search_button)
        layout.addLayout(horizontal_layout)
        layout.addStretch(1)
        
        #connect button signals to their respective functions
        self.search_button.clicked.connect(self.openImageViewer)
        self.info_button.clicked.connect(self.showAppInfo)
        
        # Elements font
        font = QFont()
        font.setPointSize(16)
        medium_font = QFont()
        medium_font.setPointSize(22)
        
        self.search_button.setFont(font)
        self.info_button.setFont(font)
        self.settings_button.setFont(medium_font)
        
        
        #Elements style
        self.setStyleSheet("background-color: #212121;color:white;")
        self.query.setFixedHeight(33)
        self.search_button.setFixedSize(36, 36) 
        self.info_button.setFixedWidth(45)
        self.settings_button.setFixedSize(45,45)

        button_style = "QPushButton { background-color: #212121; \
                                        color: white; \
                                        border: 2px solid #2e2e2e; \
                                        border-radius: 18px;padding: 5px;} \
                                        QPushButton:hover {  \
                                        background-color: #2e2e2e; }"
        
        header_buttons_style = "QPushButton { background-color: #212121; \
                                        color: #999999; \
                                        border: 2px solid #212121; \
                                        border-radius: 18px;padding: 5px;} \
                                        QPushButton:hover {  \
                                        background-color: #2e2e2e; }"
        
        qline_style = (
            "QLineEdit { \
             background-color: #212121; \
             color: white; \
             border-radius: 15px; \
             padding: 5px; \
             border: 2px solid #2e2e2e; \
             font-size: 12pt; \
             }"
        )
        
        self.search_button.setStyleSheet(button_style) 
        self.info_button.setStyleSheet(header_buttons_style)
        self.settings_button.setStyleSheet(header_buttons_style)   
        self.query.setStyleSheet(qline_style)
        completer.popup().setStyleSheet("background-color: #2e2e2e; \
                                        color: white; \
                                        font-size: 12pt;")

        
        
        self.show()

    def openImageViewer(self):
        self.selectImages()
            
        if self.result:
            self.viewer = ImageViewer(self.result, self)
            self.viewer.finishedSignal.connect(self.showMainWidget)
            self.viewer.show()
            self.hide()
        

    def showMainWidget(self):
        """
        Show the main widget when the ImageViewer is closed
        Args:
            None
        Returns:
            None
        """
        self.show()
        
        
    def selectImages(self):
        self.queryText=self.query.text()
        self.queryText=self.suggestClasses(self.queryText)
        if self.queryText==None:
            self.showErrorMessage("No images found (⌣̩̩́_⌣̩̩̀)")
            
        db=pd.read_csv("log.csv")
        self.result=db[db["class"]==self.queryText]["directory"].to_list()
                
    
    
    def suggestClasses(self,query):
        '''
        find the levenshtein distance between existing classes and 
        the search query and returns the classes with distance <= 2
        Args:
            query (str)
        Returns: 
            suggested class (str) or None
        '''
        classes=['plane','car','cat','dog','food','sea','documents']
        query=query.lower()
        
        #check for exact match
        if query in classes:
            return query
        #check for lev distance of 1 with avg words length
        for classi in classes:
            if lev_distance(query,classi)==1:
                return classi
        
        #check for lev distance of 2 with long words i.e >=8
        for classi in list(filter(lambda x: len(x) >= 8, classes)):
            if lev_distance(query,classi)==2:
                return classi
        
        #No matches returned.
        return None
    
    
    def keyPressEvent(self, event):
        """
        Event handler for key press events, overriding the base class method.

        Args:
            event (QKeyEvent): The key event object containing information about the key press.

        Returns:
            None
        """
        
        if (event.key() == Qt.Key_Return) or (event.key() == Qt.Key_Enter):
            self.openImageViewer()
            
    def showErrorMessage(self,msg):
        """
        Displays a QMessageBox warning
        Args:
            msg (str)
        Returns:
            None
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(msg)
        msg_box.setWindowTitle('Warning')
        msg_box.exec_()
        
    def showAppInfo(self):
        """
        Displays a QMessageBox containing application information such as maintainers 
        and supported classes
        
        Args:
            None
        Returns:
            None
        """
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText(f"This application is created and maintained by \
Mahmoud gamal \
        current supported search classes are {', '.join(classesNames)}")
        msg_box.setWindowTitle('info')
        msg_box.exec_()

class ImageViewer(QWidget):
    finishedSignal = pyqtSignal()
    def __init__(self, result, main_widget):
        super().__init__()

        self.file_list = []
        self.current_index = 0
        self.primary_screen = QDesktopWidget().screenGeometry()
        self.screen_width = self.primary_screen.width()
        self.screen_height = self.primary_screen.height()
        self.result = result
        self.edit_history=[]
        self.main_widget = main_widget  
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Image Viewer')
        self.setGeometry(300, 0, 750, 550)
        self.setStyleSheet("background-color: #212121;")
        
        self.image_view = QGraphicsView(self)
        self.image_view.setAlignment(Qt.AlignCenter)
        self.image_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.image_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.scene = QGraphicsScene()
        self.image_view.setScene(self.scene)
        
        # this is to fix weird behaviour similar to stackoverflow Q #68182395
        QTimer.singleShot(0, self.handle_timeout)
        self.image_view.wheelEvent = self.zoom_image

        
        self.keylist = []
        self.file_list = []
        self.current_index = 0
        self.setMouseTracking(True)
        self.load_images()

        # Main layout using QVBoxLayout
        layout = QVBoxLayout(self)
        Hlayout=QHBoxLayout(self)
        header_layout=QHBoxLayout()
        editing_buttons_layout = QHBoxLayout(self)

       
        self.leftBrowse = QPushButton('〈', self)
        self.rightBrowse = QPushButton('〉', self)
        self.back_button = QPushButton('↩', self)
        
        #SCF_icon = qta.icon("fa5s.search-location",color="white")  # Use the correct icon name here
        SCF_icon = qta.icon("mdi.folder-search-outline",color="white")  # Use the correct icon name here
        
        self.show_containing_folder_button=QPushButton(SCF_icon,'')
        self.show_containing_folder_button.setIconSize(SCF_icon.actualSize(QSize(20,  20)))  # Set the size of the icon
        Hlayout.addWidget(self.leftBrowse)
        Hlayout.addWidget(self.image_view)
        Hlayout.addWidget(self.rightBrowse)

        header_layout.addWidget(self.back_button)
        header_layout.addStretch(1)
        header_layout.addWidget(self.show_containing_folder_button)
        
        self.sharpen_button = QPushButton('Sharpen', self)
        self.gray_button = QPushButton()
        self.gaussianBlur_button = QPushButton()
        self.rotate_button = QPushButton()
        self.set_exposure_button = QPushButton('Exposure', self)
        self.remove_bg_button = QPushButton('Remove Background', self)
        
        self.undo_button=QPushButton()
        self.revert_button = QPushButton('Revert', self)
        
        self.save_button = QPushButton()
        save_icon = qta.icon('fa5.save', color='white')
        undo_icon = qta.icon('mdi.undo-variant', color='white')
        rotate_icon = qta.icon('mdi.crop-rotate', color='white')
        gray_icon=qta.icon('mdi.image-filter-black-white',color='white',scale_factor=1.4)
        blur_icon=qta.icon('mdi.blur',color='white',scale_factor=1.5)
        
        self.save_button.setIcon(save_icon)
        self.undo_button.setIcon(undo_icon)
        self.rotate_button.setIcon(rotate_icon)
        self.gray_button.setIcon(gray_icon)
        self.gaussianBlur_button.setIcon(blur_icon)
        #self.gaussianBlur_button.setIconSize(QSize(32,  32))

        self.rotate_button.setToolTip('rotate')
        
        self.exposure_slider = QSlider(Qt.Horizontal)
        self.exposure_slider.setMinimum(0)
        self.exposure_slider.setMaximum(200)
        self.exposure_slider.setValue(100)  # Set an initial value
        self.exposure_slider.valueChanged.connect(self.update_exposure)
        self.exposure_slider.hide()
        
        
        editing_buttons=[self.sharpen_button,self.gray_button,
                self.gaussianBlur_button,self.rotate_button,self.set_exposure_button ,
                 self.remove_bg_button,self.revert_button,self.undo_button,self.save_button
                ]
        navigation_buttons=[self.leftBrowse,self.rightBrowse ,self.back_button,self.show_containing_folder_button]
        
        #setting focus policy for all buttons
        for button in editing_buttons+navigation_buttons:
            button.setFocusPolicy(Qt.NoFocus)

        
        self.image_view.setFocusPolicy(Qt.NoFocus)
        #adding editing buttons to th editing buttons layout2+++++++
        for  button in editing_buttons:
            button.setFixedHeight(40)

            editing_buttons_layout.addWidget(button)
   
        layout.addLayout(header_layout)
        layout.addLayout(Hlayout)
        layout.addWidget(self.exposure_slider)
        layout.addLayout(editing_buttons_layout)
        self.setLayout(layout)

        # Connect button signals to their respective functions
        
        self.sharpen_button.clicked.connect(self.sharpen_image)
        self.gray_button.clicked.connect(self.BGR2GRAY)
        self.gaussianBlur_button.clicked.connect(self.gaussianBlur)
        self.rotate_button.clicked.connect(self.rotateCCW)
        self.set_exposure_button.clicked.connect(self.toggle_exposure_slider)
        self.save_button.clicked.connect(self.save_image)
        self.back_button.clicked.connect(self.goHome)
        self.remove_bg_button.clicked.connect(self.removeBackground)
        self.undo_button.clicked.connect(self.undo)
        self.revert_button.clicked.connect(self.revert)
        self.leftBrowse.clicked.connect(self.next_image)
        self.rightBrowse.clicked.connect(self.previous_image)
        self.show_containing_folder_button.clicked.connect(self.show_containing_folder)
        ###############################
        
        self.rightBrowse.enterEvent = self.on_enter_event
        self.rightBrowse.leaveEvent = self.on_leave_event
        self.leftBrowse.enterEvent = self.on_enter_event
        self.leftBrowse.leaveEvent = self.on_leave_event
      
        # ---------------Setting styles----------------------------
        mediumFont = QFont()
        mediumFont.setPointSize(16)
        bigFont = QFont()
        bigFont.setPointSize(20)
        
        #self.back_button.setFont(mediumFont)
        self.leftBrowse.setFont(bigFont)
        self.rightBrowse.setFont(bigFont)
        
        button_style = "QPushButton { background-color: #212121; color: white;border-left:none; border-right: none; border-top: none; border-bottom: none; } \
                        QPushButton:hover {background-color: #00347d; }"
        for button in editing_buttons:
            button.setStyleSheet(button_style)
        
        
        
        header_buttons_style=(
            "QPushButton {background-color: rgba(22, 22, 22, .5); \
            border: none; \
            color: white; \
            font-size: 16pt;} \
            QPushButton:hover {background-color: #2e2e2e;} "
        )
        self.back_button.setStyleSheet(header_buttons_style)
        self.show_containing_folder_button.setStyleSheet(header_buttons_style)
        
        self.back_button.setFixedSize(60,40) 
        self.show_containing_folder_button.setFixedSize(60,40)
        self.leftBrowse.setFixedSize(60, self.height())
        self.rightBrowse.setFixedSize(60, self.height())

        browsing_buttons_style= "background-color: rgba(22, 22, 22, .5); \
                                                    color: white; \
                                                    border: none;"
        self.leftBrowse.setStyleSheet(browsing_buttons_style)
        self.rightBrowse.setStyleSheet(browsing_buttons_style)

        self.image_view.setStyleSheet("border: none;")
        
        
        
        self.set_transparency(0)
        self.load_images()
        self.show_image()
        self.show()
      

    def load_images(self):
        self.file_list = self.result
        
    def show_image(self):
        if self.file_list:
            image_path = self.file_list[self.current_index]
            pixmap = QPixmap(image_path)

            # Clear the scene before adding a new item
            self.scene.clear()

            # Add a QGraphicsPixmapItem to the scene
            pixmap_item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(pixmap_item)

        
            
            # Set the scene rect to match the pixmap size
            self.scene.setSceneRect(pixmap_item.boundingRect())

            # Fit the image to the view
            self.image_view.fitInView(pixmap_item, Qt.KeepAspectRatio)


            self.setWindowTitle(f'Image Viewer - {os.path.basename(image_path)}')



    def show_edited_image(self):
        self.scene.clear()
        pixmap = QPixmap(self.convert_cv_image_to_qpixmap(self.edited_image))

        # Clear the scene before adding a new item
        #

        # Add a QGraphicsPixmapItem to the scene
        pixmap_item = QGraphicsPixmapItem(pixmap)
        self.scene.addItem(pixmap_item)

        # Set the scene rect to match the pixmap size
        self.scene.setSceneRect(pixmap_item.boundingRect())

        # Fit the image to the view
        self.image_view.fitInView(pixmap_item, Qt.KeepAspectRatio)

        
    def handle_timeout(self):
        if self.file_list:
            image_path = self.file_list[self.current_index]
            pixmap = QPixmap(image_path)
            pixmap_item = QGraphicsPixmapItem(pixmap)

            self.image_view.fitInView(pixmap_item, Qt.KeepAspectRatio)
        
    def zoom_image(self, event):
        # Get the current transformation matrix of the view
        transform = self.image_view.transform()

        # Set the transformation anchor to the center of the view
        self.image_view.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)

        # Get the zoom factor
        delta = event.angleDelta().y() / 120  # Get the scroll steps (typically 120 per step)
        zoom_factor = 1.1 if delta > 0 else 0.9  # Define the zoom factor

        # Scale the view using zoom_factor
        transform.scale(zoom_factor, zoom_factor)

        # Apply the new transformation to the view
        self.image_view.setTransform(transform)


    def keyPressEvent(self, event):
        
        #Navigating images in the directory
        if event.key() == Qt.Key_Right:
            self.next_image()
        elif event.key() == Qt.Key_Left:
            self.previous_image()
    
        if (event.key() == Qt.Key_Backspace) or (event.key() == Qt.Key_Escape):
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
        
    def sharpen_image(self):
            if hasattr(self, 'edited_image'):
                img=self.edited_image
            else :
                image_path = self.file_list[self.current_index]
                img = cv2.imread(image_path)
            
            gaussian_blurred=cv2.GaussianBlur(img,(5,5),1)
            sharpened=cv2.addWeighted(img,1.5,gaussian_blurred,-.5,0)
            self.edited_image=sharpened
            self.edit_history.append(self.edited_image)
            self.show_edited_image()
    def  BGR2GRAY(self):
        if hasattr(self, 'edited_image'):
            img=self.edited_image
        else :
            image_path = self.file_list[self.current_index]
            img = cv2.imread(image_path)
        
        gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        gray_3C=cv2.merge([gray,gray,gray])
        self.edited_image=gray_3C
        self.edit_history.append(self.edited_image)
        self.show_edited_image()
        
        
    def gaussianBlur(self):
        if hasattr(self, 'edited_image'):
            img=self.edited_image
        else :
            image_path = self.file_list[self.current_index]
            img = cv2.imread(image_path)
        
        Blurred_img=cv2.GaussianBlur(img,ksize=(3,3),sigmaX=1)
        self.edited_image=Blurred_img
        self.edit_history.append(self.edited_image)
        self.show_edited_image()
        
        
    def rotateCCW(self):
        if hasattr(self, 'edited_image'):
            img=self.edited_image
        else :
            image_path = self.file_list[self.current_index]
            img = cv2.imread(image_path)
        
        rotatedImg=cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        self.edited_image=rotatedImg
        self.edit_history.append(self.edited_image)
        self.show_edited_image()
        

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
        self.edit_history.append(self.edited_image)
        self.show_edited_image()
    
    def removeBackground(self):
        if hasattr(self, 'edited_image'):
            img=self.edited_image
        else :
            image_path = self.file_list[self.current_index]
            img = cv2.imread(image_path)
        removed_bg_image=rembg.remove(img,bgcolor=(2555,255,0,1))
        self.edited_image=removed_bg_image
        self.show_edited_image()
        
    def convert_cv_image_to_qpixmap(self, cv_image):
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            height, width, channel = cv_image.shape
            bytes_per_line = 3 * width
            q_image = QImage(cv_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            return QPixmap.fromImage(q_image)


        
        
    def undo(self):
        if len(self.edit_history)>0:
            self.edit_history.pop()  
            self.edited_image=self.edit_history[-1]
            self.show_edited_image()
            

        else:
            if hasattr(self, 'edited_image'):
                delattr(self,'edited_image')
                self.show_image()
            
            
    def revert(self):
        if hasattr(self, 'edited_image'):
            delattr(self,'edited_image')
            self.edit_history=[]
        self.show_image()
    
    def save_image(self):
        if hasattr(self, 'edited_image'):
            msg_box = SavingMessageBox(self.file_list[self.current_index],self.edited_image)
            msg_box.exec_()
            delattr(self,'edited_image')
            self.edit_history=[]
            
        else:
            self.showErrorMessage("no changes were made!")
    
    def show_success_message(self):
        '''
        Display a QMessageBox ("Saved successfully!") with information icon

        Args:
            None

        Returns:
            None
        '''
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("Saved successfully!")
        msg_box.setWindowTitle("Success")
        msg_box.exec_()
        
    
    def showErrorMessage(self,msg):
        '''
        Display a QMessageBox with a warning icon.

        Args:
            msg (str): The message to be displayed in the QMessageBox.

        Returns:
            None
        '''
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Warning)
        msg_box.setText(msg)
        msg_box.setWindowTitle('Warning')
        msg_box.exec_()
    
    def goHome(self):
        '''
        Close the current widget (ImageViewer)
        
        Args:
            None
            
        Returns:
            None
        '''
        
        self.close()
        
    
    

    def show_containing_folder(self,file_path):
        image_path=self.file_list[self.current_index]
        
        dir_path=image_path[0:image_path.rfind('/')]

        commands = [
            f"xdg-open {dir_path}",      # Default for most desktop environments
            f"nautilus {dir_path}",      # Default for GNOME desktop environment
            f"nemo {dir_path}",          # Default for Cinnamon desktop environment
            f"thunar {dir_path}"         # Default for XFCE desktop environment
        ]

        for command in commands:
            try:
                subprocess.run(command.split(), check=True)
                return True
            except subprocess.CalledProcessError:
                continue

        # If none of the commands were successful
        print("Unable to open file manager")
        return False



    
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
        
        
        
class SavingMessageBox(QMessageBox):
    def __init__(self, image_path, edited_image, *args, **kwargs):
        super(SavingMessageBox, self).__init__(*args, **kwargs)

        self.image_path=image_path
        self.edited_image=edited_image
        self.overwrite_button = QPushButton("Overwrite")
        self.copy_button = QPushButton("Copy")
       
        self.addButton(self.overwrite_button, QMessageBox.ActionRole)
        self.addButton(self.copy_button, QMessageBox.ActionRole)
                       
        
        self.overwrite_button.clicked.connect(self.handle_overwrite)
        self.copy_button.clicked.connect(self.handle_copy)
        
        #################

       
        self.setWindowTitle("Save Image")
        self.setText("Do you want to overwrite the existing image or save a copy?")
        self.setStyleSheet("background-color: #212121;color:white;")
        self.overwrite_button.setStyleSheet("QPushButton:hover {background-color: #cc0e14; }")
        self.copy_button.setStyleSheet("QPushButton:hover {background-color: #0e90cc; }")

    def handle_overwrite(self):
        cv2.imwrite(self.image_path, self.edited_image)
        print(self.image_path)
    def handle_copy(self):
        mod_time = datetime.datetime.now().strftime("%Y-%m-%d-%H:%M:%S")
        cv2.imwrite(f"{os.path.splitext(self.image_path)[0]}_{mod_time}.jpg",
                    self.edited_image)
        
if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #000000; border: 1px solid white; }")
    
    
    
    
    
    


    
    
    
    
    
    main_widget = MainWidget()

    app.exec_()

