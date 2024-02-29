import os
import time
import datetime
import subprocess
import glob
import numpy as np
import pandas as pd
import cv2
from urllib.parse import urlparse
from PIL.PngImagePlugin import PngInfo
from PIL import Image
import rembg

import qtawesome as qta
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap,QColor,QFont,QImage,QIcon
from PyQt5.QtCore import Qt,pyqtSignal,QPoint,QSize,QTimer

from Levenshtein import distance as lev_distance
from Othumbnails import ThumbnailMaker
from custom import *
from styles import *
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = '/path/to/your/qt/plugins'
from PyQt5.QtCore import pyqtSlot
classesNames=['bicycle','boat','building','bus','car','forest',
             'glacier','helicopter','motorcycle', 'mountain',
             'plane','sea','street','train','truck','cat']




class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()
    def init_ui(self):
        self.setWindowTitle('OGallery')
        self.setGeometry(300, 100, 800, 600)
        self.style=OStyle()
        #self.setWindowIcon(qta.icon('fa5s.map-pin',color=self.style.color.dark_background,
        #                            scale_factor=1.2))
        self.setWindowIcon(QIcon(QPixmap('icon.png')))
        #buttons instantiation
        self.query_line = QLineEdit(self)
        self.search_button = QPushButton()
        
        self.info_button=QPushButtonHighlight()
        self.settings_button=QPushButtonHighlight()
        self.gallery_button=QPushButtonHighlight()
       
        #Autocomplete using QCompleter
        completer = QCompleter(classesNames, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.query_line.setCompleter(completer)
        
        #logo QLabel instantiation and settings
        self.logo_label = QLabel(self)
        pixmap = QPixmap('l2.jpg')
        self.logo_label.setPixmap(pixmap)
        self.logo_label.setAlignment(Qt.AlignCenter)
        
        #layout structure 
        layout = QVBoxLayout(self)
        horizontal_layout = QHBoxLayout()
        header_layout=QHBoxLayout()
        
        header_layout.addWidget(self.settings_button)
        header_layout.addWidget(self.gallery_button)
        header_layout.addStretch(1)
        header_layout.addWidget(self.info_button)
                
        layout.addLayout(header_layout)
        layout.addWidget(self.logo_label)
        horizontal_layout.addWidget(self.search_button)
        horizontal_layout.addWidget(self.query_line)
        layout.addLayout(horizontal_layout)
        layout.addStretch(1)
        
        #connect button signals to their respective functions
        self.search_button.clicked.connect(self.openImageViewer)
        self.info_button.clicked.connect(self.showAppInfo)
        self.gallery_button.clicked.connect(self.openGallery)
        self.settings_button.clicked.connect(self.showDialog)
        
        
        #Elements style
        self.setStyleSheet(f"background-color: {self.style.color.dark_background};color:white;")
        self.query_line.setFixedHeight(33)
        self.search_button.setFixedSize(36, 36) 
        self.info_button.setFixedWidth(45)
        self.settings_button.setFixedSize(45,45)

        button_style = f"QPushButton {{ background-color: {self.style.color.dark_background}; \
                                        color: {self.style.color.foreground}; \
                                        icon-size: {self.style.size.standard_icon_size}; \
                                        border: 2px solid {self.style.color.dark_background}; \
                                        border-radius: 18px;padding: 5px;}} \
                                        QPushButton:hover {{  \
                                        background-color: {self.style.color.hover_default}; }}"
        
        
        qline_style = (
            f"QLineEdit {{ \
                background-color: {self.style.color.dark_background}; \
                color: white; \
                border-radius: 15px; \
                padding: 5px; \
                border: 2px solid {self.style.color.light_gray}; \
                font-size: 12pt; \
            }} \
            QLineEdit:focus {{ \
                border-color: {self.style.color.dark_purple}; \
            }}"
        )

        
       
        buttons=[self.search_button,self.info_button,self.settings_button,self.gallery_button]
        for button in buttons:
            button.setStyleSheet(button_style)
            
        self.query_line.setStyleSheet(qline_style)
        completer.popup().setStyleSheet(f"background-color: {self.style.color.light_gray}; \
                                        color: white; \
                                        font-size: 12pt;")

        
        #icons
        
        self.search_button.setIcon(qta.icon('fa.search',color=self.style.color.foreground))
        
        self.info_button.setIcon(qta.icon('ei.info-circle',color=self.style.color.foreground))
        self.info_button.setIconNormal(qta.icon('ei.info-circle',color=self.style.color.foreground))
        self.info_button.setIconHover(qta.icon('ei.info-circle',color=self.style.color.purple))
        
        
        self.settings_button.setIcon(qta.icon('fa.cog',color=self.style.color.foreground))
        self.settings_button.setIconNormal(qta.icon('fa.cog',color=self.style.color.foreground))
        self.settings_button.setIconHover(qta.icon('fa.cog',color=self.style.color.purple))
        
        self.gallery_button.setIcon(qta.icon('mdi.folder-image',color=self.style.color.foreground))
        self.gallery_button.setIconNormal(qta.icon('mdi.folder-image',color=self.style.color.foreground))
        self.gallery_button.setIconHover(qta.icon('mdi.folder-image',color=self.style.color.purple))
     
        self.show()

        
    def showDialog(self):
        username = os.getenv('USER')
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.selected_directory = QFileDialog.getExistingDirectory(self, "Select Directory", options=options)
        
        if self.selected_directory:
            if os.path.exists(f'/home/{username}/.cache/OpenGallery/')==False:
                os.makedirs(f'/home/{username}/.cache/OpenGallery/')
            with open(f'/home/{username}/.cache/OpenGallery/config.log', 'w') as config_file:
                config_file.write(self.selected_directory)


            with open(f'/home/{username}/.cache/OpenGallery/config.log', 'r') as config_file:
                directory = config_file.read()
            
    def openImageViewer(self):
        self.selectImages()
            
        if self.result:
            self.viewer = ImageViewer(self.result, self)
            self.viewer.finishedSignal.connect(self.showMainWidget)
            self.viewer.show()
            self.hide()
        
    def openGallery(self):
        self.image_gallery=ImageGalleryApp()
        self.image_gallery.show()
    def showMainWidget(self):
        """
        Show the main widget when the ImageViewer is closed
        Args:
            None
        Returns:
            None
        """
        self.show()
        
    
    def map_arabic_to_english(self,input_string):
        '''
        Maps Arabic characters to english characters if any exists
        Args:
            input_string (str)
        Returns:
            output_string (str)

        '''
        arabic_to_english = {
        'ض': 'q',
        'ص': 'w',
        'ث': 'e',
        'ق': 'r',
        'ف': 't',
        'غ': 'y',
        'ع': 'u',
        'ه': 'i',
        'خ': 'o',
        'ح': 'p',
        'ج': '[',
        'د': ']',
        'ش': 'a',
        'س': 's',
        'ي': 'd',
        'ب': 'f',
        'ل': 'g',
        'ا': 'h',
        'ت': 'j',
        'ن': 'k',
        'م': 'l',
        'ك': ';',
        'ط': "'",
        'ئ': 'z',
        'ء': 'x',
        'ؤ': 'c',
        'ر': 'v',
        'ﻻ': 'b',
        'ى': 'n',
        'ة': 'm',
        'و': ',',
        'ز': '.',
        'ظ': '/',
        ' ': ' ' ,

        }


        output_string = ''
        for char in input_string:
            if char in arabic_to_english:
                output_string += arabic_to_english[char]
            else:
                output_string += char
        return output_string

    def selectImages(self):
        self.queryText=self.query_line.text()
        self.queryText=self.map_arabic_to_english(self.queryText)
        self.queryText=self.suggestClasses(self.queryText)
        if self.queryText==None:
            self.showErrorMessage("No images found")
            
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
        msg_box = InfoMessageBox()
        pixmap1 = QPixmap(qta.icon('mdi.jellyfish',color='#faf7f7').pixmap(100,100))
        pixmap2 = QPixmap(qta.icon('fa.exclamation',color='#fde01a').pixmap(50,50))
        combined_pixmap = CustomAwesome().concat_pixmaps(pixmap1, pixmap2,1.5)
        msg_box.setIconPixmap(combined_pixmap)
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
        msg_box = InfoMessageBox()
        pixmap1 = QPixmap(qta.icon('mdi.jellyfish',color='#faf7f7').pixmap(100,100))
        pixmap2 = QPixmap(qta.icon('mdi.glasses',color='#000000').pixmap(50,50))
        
        msg_box.setIconPixmap(CustomAwesome().concat_pixmaps(pixmap1, pixmap2,3))
        msg_box.setText(f"current supported search classes are {', '.join(classesNames)}")
        msg_box.setWindowTitle('info')
        msg_box.exec_()


class ImageViewer(QWidget):
    finishedSignal = pyqtSignal()
    def __init__(self, result, main_widget,current_index=0,from_gallery=False):
        super().__init__()
        self.from_gallery=from_gallery
        self.style=OStyle()
        self.file_list = []
        self.current_index = current_index
        self.primary_screen = QDesktopWidget().screenGeometry()
        self.screen_width = self.primary_screen.width()
        self.screen_height = self.primary_screen.height()
        self.result = result
        self.edit_history=[]
        self.main_widget = main_widget  
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Image Viewer')
        self.setGeometry(300, 100, 750, 550)
        
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
        

        SCF_icon = qta.icon("mdi.folder-search-outline",color="white")  # Use the correct icon name here
        
        self.show_containing_folder_button=QPushButton(SCF_icon,'')
        self.show_containing_folder_button.setIconSize(SCF_icon.actualSize(QSize(20,  20)))  # Set the size of the icon
        Hlayout.addWidget(self.leftBrowse)
        Hlayout.addWidget(self.image_view)
        Hlayout.addWidget(self.rightBrowse)

        header_layout.addWidget(self.back_button)
        

        header_layout.addStretch(1)
        header_layout.addWidget(self.show_containing_folder_button)
        
        self.sharpen_button = QPushButton()
        self.gray_button = QPushButton()
        self.gaussianBlur_button = QPushButton()
        self.rotate_button = QPushButton()
        self.flip_button=QPushButton()
        self.set_exposure_button = QPushButton()
        self.blur_background_button = QPushButton()
        self.undo_button=QPushButton()
        self.compare_button=QPushButton()
        self.revert_button = QPushButton('Revert', self)
        
        self.save_button = QPushButton()
        
        #setting icons       
        self.save_button.setIcon(qta.icon('fa5.save', color='white'))
        self.undo_button.setIcon(qta.icon('mdi.undo-variant', color='white'))
        self.rotate_button.setIcon(qta.icon('mdi.crop-rotate', color='white'))
        self.gray_button.setIcon(qta.icon('mdi.image-filter-black-white',color='white'))
        self.gaussianBlur_button.setIcon(qta.icon('mdi.blur',color='white'))
        self.blur_background_button.setIcon(qta.icon('fa.user',color='white'))
        self.sharpen_button.setIcon(qta.icon('mdi.details',color='white'))
        self.set_exposure_button.setIcon(qta.icon('mdi.camera-iris',color='white'))
        self.flip_button.setIcon(qta.icon('mdi.reflect-horizontal',color='white'))
        self.compare_button.setIcon(qta.icon('mdi.select-compare',color='white'))
        
       
        #tooltip
        self.rotate_button.setToolTip('Rotate')
        self.undo_button.setToolTip('Undo')
        self.gray_button.setToolTip('Gray scale')
        self.gaussianBlur_button.setToolTip('Blur')
        self.blur_background_button.setToolTip('Portrait')
        self.flip_button.setToolTip('Flip horizontally')
        self.sharpen_button.setToolTip('Sharpen')
        self.set_exposure_button.setToolTip('Exposure')
        self.show_containing_folder_button.setToolTip('Show containing folder')
        
        self.exposure_slider = QSlider(Qt.Horizontal)
        self.exposure_slider.setMinimum(2)
        self.exposure_slider.setMaximum(200)
        self.exposure_slider.setValue(100)  
        self.exposure_slider.valueChanged.connect(self.update_exposure)
        self.exposure_slider.hide()
        
        
        editing_buttons=[self.sharpen_button,self.gray_button,
                self.gaussianBlur_button,self.rotate_button,self.flip_button,self.set_exposure_button ,
                 self.blur_background_button,self.compare_button, self.revert_button,self.undo_button,self.save_button
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
        self.flip_button.clicked.connect(self.flipH)
        self.set_exposure_button.clicked.connect(self.toggle_exposure_slider)
        self.save_button.clicked.connect(self.save_image)
        self.back_button.clicked.connect(self.goHome)

        self.blur_background_button.clicked.connect(self.blurBackground)
        self.undo_button.clicked.connect(self.undo)
        self.revert_button.clicked.connect(self.revert)
        self.leftBrowse.clicked.connect(self.previous_image)
        self.rightBrowse.clicked.connect(self.next_image)
        self.show_containing_folder_button.clicked.connect(self.show_containing_folder)
        self.compare_button.pressed.connect(self.show_image)
        self.compare_button.released.connect(self.show_edited_image)
        
        ###############################
        
        self.rightBrowse.enterEvent = self.on_enter_event
        self.rightBrowse.leaveEvent = self.on_leave_event
        self.leftBrowse.enterEvent = self.on_enter_event
        self.leftBrowse.leaveEvent = self.on_leave_event
      
        #Setting styles
        self.setStyleSheet(f"background-color: {self.style.color.background};")
        self.leftBrowse.setFont(self.style.size.large_font)
        self.rightBrowse.setFont(self.style.size.large_font)
        border_color='#242424'
        
        button_style = ("QPushButton {{"
                "background-color: #1f1f1f; "
                "color: white; "
                "icon-size:{icon_size};"
                "border-top: 2px solid {border_color}; "
                "border-bottom: 2px solid {border_color}; "
                "border-right: 2px solid {border_color}; "
                "border-left: 2px solid {border_color}; "
                "}} "
                "QPushButton:hover {{"
                "background-color: #00347d; "
                "}}").format(border_color=border_color,icon_size=self.style.size.standard_icon_size)

        
        
        for button in editing_buttons:
            button.setStyleSheet(button_style)
        
        
        
        button_style=(
            "QPushButton {background-color: rgba(22, 22, 22, .5); \
            border: none; \
            color: white; \
            font-size: 16pt;} \
            QPushButton:hover {background-color: #2e2e2e;} "
        )
        self.back_button.setStyleSheet(button_style)
        self.show_containing_folder_button.setStyleSheet(button_style)
        
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
        try:
            self.scene.clear()
            pixmap = QPixmap(self.convert_cv_image_to_qpixmap(self.edited_image))




            # Add a QGraphicsPixmapItem to the scene
            pixmap_item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(pixmap_item)

            # Set the scene rect to match the pixmap size
            self.scene.setSceneRect(pixmap_item.boundingRect())

            # Fit the image to the view
            self.image_view.fitInView(pixmap_item, Qt.KeepAspectRatio)
        except:
            self.show_image()
        

        
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
        
        if event.key()==Qt.Key_Delete:
            self.delete_image()
            
        #saving edited images using key event ctrl&s
        if event.key()== Qt.Key_Control:
            self.keylist.append(Qt.Key_Control)
            
            
        if event.key()==Qt.Key_S :
            self.keylist.append(Qt.Key_S)
            
        
        if len(self.keylist)==2:
            if (self.keylist[0]*self.keylist[1])==Qt.Key_Control*Qt.Key_S:
                self.save_image()
         
        
    def keyReleaseEvent(self, event):
        time.sleep(.2)
        self.keylist=[] 
        
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
        self.set_transparency(.5)

    def on_leave_event(self, event):
        self.set_transparency(0)
     
    def copyToClipboard(self):
        image_path = self.file_list[self.current_index]
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(QPixmap(image_path))
        
        
        
        
        
        
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
        
    def flipH(self):
        if hasattr(self, 'edited_image'):
            img=self.edited_image
        else :
            image_path = self.file_list[self.current_index]
            img = cv2.imread(image_path)
        
        flipped_img=cv2.flip(img, 1)
        self.edited_image=flipped_img
        self.edit_history.append(self.edited_image)
        self.show_edited_image()
    
    def toggle_exposure_slider(self):
    # Toggle the visibility of the slider when the button is pressed
        self.exposure_slider.setVisible(not self.exposure_slider.isVisible())
        colors=['#1f1f1f','#00347d']
        border_color='#242424'
        exposure_button_style=f"QPushButton {{ background-color: {colors[self.exposure_slider.isVisible()]}; color: white;border-top: 2px solid {border_color};border-bottom: 2px solid {border_color};border-right: 2px solid {border_color}; border-left: 2px solid {border_color};}}"
        self.set_exposure_button.setStyleSheet(exposure_button_style)
       
    
    def update_exposure(self, gamma1e2):

        
        
        if hasattr(self, 'exposureImg'):
            if len(self.edit_history)==1:
                img=self.edit_history[-1]
                
            if len(self.edit_history)>1:
                self.edit_history.pop()
                self.exposureImg=self.edit_history[-1]
                img=self.exposureImg
            
        elif hasattr(self, 'edited_image'):
            img=self.edited_image
        else :
            image_path = self.file_list[self.current_index]
            img = cv2.imread(image_path)
        gamma=gamma1e2/100
        invGamma = 1.0 / gamma
        table = np.array([((i / 255.0) ** invGamma) * 255
            for i in np.arange(0, 256)]).astype("uint8")
        self.exposureImg= cv2.LUT(img, table)
        
        self.edited_image=self.exposureImg
        self.edit_history.append(self.edited_image)
        self.show_edited_image()
        
    def blurBackground(self):
        if hasattr(self, 'edited_image'):
            img=self.edited_image
        else :
            image_path = self.file_list[self.current_index]
            img = cv2.imread(image_path)
        mask = rembg.remove(img,only_mask=True)
        mask_3c=cv2.merge([mask,mask,mask])
        foreground = np.copy(img).astype(float)
        background = cv2.blur(img,(9,9)).astype(float)
        alpha = mask_3c
        alpha = alpha.astype(float)/255
        foreground = cv2.multiply(alpha, foreground)
        background = cv2.multiply(1.0 - alpha, background)
        blurred_bg_image = cv2.add(foreground, background)/255
        blurred_bg_image = (blurred_bg_image * 255).astype(np.uint8)
        self.edited_image=blurred_bg_image
        self.show_edited_image()
        
    def convert_cv_image_to_qpixmap(self, cv_image):
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            height, width, channel = cv_image.shape
            bytes_per_line = 3 * width
            q_image = QImage(cv_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
            return QPixmap.fromImage(q_image)


        
        
    def undo(self):
        if len(self.edit_history)>1:
            
            self.edit_history.pop()  
            self.edited_image=self.edit_history[-1]
            self.show_edited_image()
            

        else:
            if hasattr(self, 'edited_image'):
                self.edit_history=[]
                delattr(self,'edited_image')
                if hasattr(self,'exposureImg'):
                    delattr(self,'exposureImg')
                self.show_image()
            
            
    def revert(self):
        if hasattr(self, 'edited_image'):
            delattr(self,'edited_image')
            if hasattr(self,'exposureImg'):
                    delattr(self,'exposureImg')
        self.exposure_slider.setValue(100)
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
    
    def delete_image(self):
        if os.path.exists(self.file_list[self.current_index]):
            os.remove(self.file_list[self.current_index])
            self.next_image()
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
        msg_box = InfoMessageBox()
        pixmap1 = QPixmap(qta.icon('mdi.jellyfish',color='#faf7f7').pixmap(100,100))
        pixmap2 = QPixmap(qta.icon('mdi.fullscreen-exit',color='#e2172b').pixmap(50,50))
        combined_pixmap = CustomAwesome().concat_pixmaps(pixmap1, pixmap2,2)
        msg_box.setIconPixmap(combined_pixmap)
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
        if self.from_gallery:
            self.image_gallery=ImageGalleryApp()
            self.image_gallery.show()
    
    

    def show_containing_folder(self,file_path):
        image_path=(self.file_list[self.current_index])
        dir_path=image_path[0:image_path.rfind('/')]

        commands = [
            f"nautilus --select",  # Default for GNOME desktop environment            f"nemo {dir_path}",          # Default for Cinnamon desktop environment
            f"xdg-open",      # Default for most desktop environments
            f"thunar"         # Default for XFCE desktop environment
        ]
        
        for command in commands:
            try:
                command_run=command.split()
                if command=='nautilus --select':
                    command_run.append(image_path)
                else:
                    command_run.append(dir_path)
                
                subprocess.run(command_run, check=True)
                return True
            except subprocess.CalledProcessError:
                continue

        # If none of the commands were successful
        return False



    
    def closeEvent(self, event):
        # Override the closeEvent method to handle the window close event
        self.finishedSignal.emit()
        event.accept()


class ImageThumbnailWidget(QWidget):
    thumbnailClicked = pyqtSignal()
    def __init__(self, image_path,image_files):
        super().__init__()
        username = os.getenv('USER')
        self.cache_dir = f"/home/{username}/.cache/OpenGallery/"
        self.style=OStyle()
        self.image_path = image_path
        self.image_files=image_files
        
        self.init_ui()
    def init_ui(self):
        layout = QVBoxLayout()
        tm=ThumbnailMaker(self.cache_dir)
        self.setStyleSheet(f"background-color: {self.style.color.background};")
        thumbnail_name=tm.compute_md5(tm.add_file_scheme(self.image_path))+".png"
        thumbnail_path=self.cache_dir+thumbnail_name
        
        if os.path.exists(thumbnail_path):
            thumb_pil=Image.open(thumbnail_path)
            thumb_MTime=int(float(thumb_pil.info['Thumb::MTime']))
            image_MTime=int(os.path.getmtime(self.image_path))
            if image_MTime==thumb_MTime:
                pixmap = QPixmap(thumbnail_path)
        
            else:
                tm.create_thumbnail(self.image_path)
                pixmap = QPixmap(thumbnail_path)
       
        else:
            tm.create_thumbnail(self.image_path)
            pixmap = QPixmap(thumbnail_path)
            
        pixmap = pixmap.scaledToWidth(200)  
        self.label = QLabel()
        self.label.setPixmap(pixmap)
        self.label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.label)
        self.setLayout(layout)

    def enterEvent(self, event):
        self.setStyleSheet(f"background-color: {self.style.color.hover_default};")

    def leaveEvent(self, event):
        self.setStyleSheet(f"background-color: {self.style.color.background};")

    def mousePressEvent(self, event):
        self.setStyleSheet(f"background-color: {self.style.color.royal_blue};")
        self.viewer = ImageViewer(self.image_files, main_widget,
                                  current_index=self.image_files.index(self.image_path),
                                 from_gallery=True)
        self.thumbnailClicked.emit()
    def mouseReleaseEvent(self, event):
            self.setStyleSheet(f"background-color: {self.style.color.background};")
            
            
    

class ImageGalleryApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.style=OStyle()
        
        self.file_types=['jpg','jpeg','png','gif']

        self.init_ui()
        
    def init_ui(self):
        #layout
        central_widget = QWidget()
        self.setStyleSheet(f"background-color: {self.style.color.background};")
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget(scroll_area)
        scroll_area.setWidget(scroll_content)
        layout = QGridLayout()
        scroll_content.setLayout(layout)
        
        username = os.getenv('USER')
        with open(f'/home/{username}/.cache/OpenGallery/config.log', 'r') as config_file:
                images_directory = config_file.read()
        image_files=[]
        for file_type in self.file_types:
            image_files+=(glob.glob(f"{images_directory}/**/*.{file_type}",
                                    recursive=True))
        image_files.sort(key=lambda x: os.path.getmtime(x),reverse=True)

        row, col = 0, 0
        for index, image_file in enumerate(image_files):
            thumbnail_widget = ImageThumbnailWidget(image_file,image_files)
            thumbnail_widget.thumbnailClicked.connect(self.close)
            layout.addWidget(thumbnail_widget, row, col)
            
            col += 1
            if col == round(self.width()/200):
                col = 0
                row += 1

        central_widget.setLayout(layout)
        scroll_area.setWidget(central_widget)
        self.setCentralWidget(scroll_area)

        self.setGeometry(300, 100, 800, 650)
        self.setWindowTitle('OGallery')
        self.show()
    
    def keyPressEvent(self, event):
            if (event.key() == Qt.Key_Backspace) or (event.key() == Qt.Key_Escape):
                self.close()
    
if __name__ == '__main__':
    app = QApplication([])
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #000000; border: 1px solid white; }")
    
    
    

    


    
    
    main_widget = MainWidget()
    
    app.exec_()

