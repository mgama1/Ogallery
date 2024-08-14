import yaml
import webbrowser
from pyzbar.pyzbar import decode as decodeqr

import multiprocessing
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
from MobileNet import Model
import qtawesome as qta
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap,QColor,QFont,QImage,QIcon,QCursor,QDesktopServices
from PyQt5.QtCore import Qt,pyqtSignal,QPoint,QSize,QTimer,QStringListModel,QObject,QEvent,QUrl    

from itertools import chain

from Levenshtein import distance as lev_distance
from Othumbnails import ThumbnailMaker
from custom import *
from core import *
#os.environ['QT_QPA_PLATFORM'] = 'wayland'
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = '/path/to/your/qt/plugins'
from PyQt5.QtCore import pyqtSlot

from MobileNet import Model


class MainWidget(QWidget):
    def __init__(self):
        super().__init__()
        with open('config.yaml', 'r') as file:
            self.config_data = yaml.safe_load(file)
        self.init_ui()


    def init_ui(self):
        self.setWindowTitle('OGallery')
        self.setGeometry(300, 100, 750, 500)

        
        #self.model=Model()
        with open('classes_synonyms.yaml', 'r') as file:
            classes_synonyms = yaml.safe_load(file)
        # Flatten keys and values of model.classes_synonyms
        self.classes_plus = chain(classes_synonyms.keys(), classes_synonyms.values())
        # Split, strip, and filter empty strings.
        self.classes_plus = [item.strip().replace("q_",'') for cls in self.classes_plus for item in cls.split(',') if item.strip()] 
        

        self.setWindowIcon(QIcon('media/iconc.ico'))
        
        config_file_path = 'config.yaml'
        
        if not os.path.exists(config_file_path):
            with open(config_file_path, 'w') as file:
                initial_data = {'style_color': '#8c40d4'}
                yaml.dump(initial_data, file)
        with open(config_file_path, 'r') as file:
            self.config_data = yaml.safe_load(file)
        
        self.loadBackground()
        
        #buttons instantiation
        self.query_line = QLineEdit(self)
        self.query_line.setMinimumWidth(500)
        self.search_button = QPushButtonHighlight()
        
        self.info_button=QPushButtonHighlight()
        self.settings_button=QPushButtonHighlight()
        self.gallery_button=QPushButtonHighlight()
       
        #Autocomplete using QCompleter
        
              
        completer = QCompleter(self.classes_plus, self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.query_line.setCompleter(completer)
        
        
        
        #layout structure 
        layout = QVBoxLayout(self)
        horizontal_layout = QHBoxLayout()
        header_layout=QHBoxLayout()
        
        header_layout.addWidget(self.settings_button)
        header_layout.addWidget(self.gallery_button)
        header_layout.addStretch(1)
        header_layout.addWidget(self.info_button)
                
        layout.addLayout(header_layout)
        #layout.addWidget(self.logo_label)
        horizontal_layout.addStretch(1)
        horizontal_layout.addWidget(self.search_button)
        horizontal_layout.addWidget(self.query_line)
        horizontal_layout.addStretch(1)
        layout.addStretch(2)
        layout.addLayout(horizontal_layout)
        layout.addStretch(1)
        
        #connect button signals to their respective functions
        self.search_button.clicked.connect(self.openResultsGallery)
        self.info_button.clicked.connect(self.showAppInfo)
        self.gallery_button.clicked.connect(self.openGallery)
        self.settings_button.clicked.connect(self.openSettings)
        
        
        #Elements style
        self.setStyleSheet(f"background-color: {self.config_data['dark_background']};color:white;")
        self.query_line.setFixedHeight(33)
        self.search_button.setFixedSize(36, 36) 
        self.info_button.setFixedWidth(45)
        self.settings_button.setFixedSize(40,40)
        self.gallery_button.setFixedSize(40,40)
        self.info_button.setFixedSize(40,40)


        button_style = f"QPushButton {{ background-color: transparent; \
                                        color: {self.config_data['foreground']}; \
                                        icon-size: {self.config_data['standard_icon_size']}; \
                                        border: none ;\
                                        border-radius: 16px;padding: 0px;}} \
                                        QPushButton:hover {{  \
                                        background-color: {self.config_data['foreground']}; }}"
        
        
        qline_style = (
            f"QLineEdit {{ \
                background-color: {self.config_data['dark_background']}; \
                color: white; \
                border-radius: 15px; \
                padding: 5px; \
                border: 2px solid {self.config_data['light_gray']}; \
                font-size: 12pt; \
            }} \
            QLineEdit:focus {{ \
                border-color: {self.config_data['hover_default']}; \
            }}"
        )

        
       
        buttons=[self.search_button,self.info_button,self.settings_button,self.gallery_button]
        for button in buttons:
            button.setStyleSheet(button_style)
            
        self.query_line.setStyleSheet(qline_style)
        completer.popup().setStyleSheet(f"background-color: {self.config_data['light_gray']}; \
                                        color: white; \
                                        font-size: 12pt;")

        
        #icons
        
        self.search_button.setIconNormal(qta.icon('fa.search',color='#212121',scale_factor=1.1))
        self.search_button.setIconHover(qta.icon('fa.search',color=self.config_data["style_color"],scale_factor=1.1))
        
        self.info_button.setIconNormal(qta.icon('ei.info-circle',color=self.config_data['foreground']))
        self.info_button.setIconHover(qta.icon('ei.info-circle',color=self.config_data["style_color"]))
        
        
        self.settings_button.setIconNormal(qta.icon('fa.cog',color=self.config_data['foreground']))
        self.settings_button.setIconHover(qta.icon('fa.cogs',color=self.config_data["style_color"]))
        
        self.gallery_button.setIconNormal(qta.icon('mdi.folder-image',color=self.config_data['foreground']))
        self.gallery_button.setIconHover(qta.icon('mdi.folder-image',color=self.config_data["style_color"]))
     
        self.show()


    def loadBackground(self):
        
        
        color=self.config_data["style_color"]
        pixmap = QPixmap(f'media/{color}.png')
        
            
        self.background_label = QLabel(self)
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True) 
        self.background_label.setGeometry(0, 0, self.width(), self.height())

    def updateBackground(self,color):
        print(f"color sent {color}")
        pixmap = QPixmap(f'media/{color}.png')
        self.background_label.setPixmap(pixmap)
        self.search_button.setIconHover(qta.icon('fa.search',color=color,scale_factor=1.1))
        self.info_button.setIconHover(qta.icon('ei.info-circle',color=color))
        self.settings_button.setIconHover(qta.icon('fa.cogs',color=color))
        self.gallery_button.setIconHover(qta.icon('mdi.folder-image',color=color))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'background_label'):
            self.background_label.setGeometry(0, 0, self.width(), self.height())
            
    def openSettings(self):
        self.settings=SettingsWidget()
        self.settings.colorChanged.connect(self.updateBackground)
        self.settings.show()
    
           
    def openResultsGallery(self):
        if self.selectImages():
                
            if self.result:
                core=Core()
                self.image_gallery=ImageGalleryApp(self.result)
                self.image_gallery.show()
                
    def openGallery(self):
        core=Core()
        self.image_gallery=ImageGalleryApp(core.getImagesPaths())
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
        if self.queryText=='':
            self.showErrorMessage("No images found")
            return 0
            
        db=pd.read_csv("db.csv")
        
        self.result=db[db["class"].str.contains("q_"+self.queryText) | db["synonyms"].str.contains("q_"+self.queryText) ]["directory"].to_list()
        return 1
    
    
        
        
    def suggestClasses(self,query):
        '''
        find the levenshtein distance between existing classes and 
        the search query and returns the classes with distance <= 2
        Args:
            query (str)
        Returns: 
            suggested class (str) or None
        '''
        classes=[class_.lower().replace("q_",'') for class_ in self.classes_plus] 
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
        return ''
    
    
    def keyPressEvent(self, event):
        """
        Event handler for key press events, overriding the base class method.

        Args:
            event (QKeyEvent): The key event object containing information about the key press.

        Returns:
            None
        """
        
        if (event.key() == Qt.Key_Return) or (event.key() == Qt.Key_Enter):
            self.openResultsGallery()
            
    def showErrorMessage(self,msg):
        """
        Displays a QMessageBox warning
        Args:
            msg (str)
        Returns:
            None
        """
        msg_box = InfoMessageBox()
        pixmap = QPixmap('media/warning.png').scaledToWidth(150)
        msg_box.setIconPixmap(pixmap)
        msg_box.setText(msg)
        msg_box.setWindowTitle('Warning')
        msg_box.exec_()
        
    def showAppInfo(self):
        """
        Displays a 
        
        Args:
            None
        Returns:
            None
        """
        self.info=InfoWidget()
        self.info.show()


class ImageViewer(QWidget):
    finishedSignal = pyqtSignal()
    savedSignal=pyqtSignal(dict)
    deletedSignal=pyqtSignal(dict)
    def __init__(self, result,current_index=0):
        super().__init__()
        self.NAVBUTTONWIDTH=60
        with open('config.yaml', 'r') as file:
            self.config_data = yaml.safe_load(file)
        self.file_list = []
        self.current_index = current_index
        self.primary_screen = QDesktopWidget().screenGeometry()
        self.screen_width = self.primary_screen.width()
        self.screen_height = self.primary_screen.height()
        self.result = result
        self.edit_history=[]
        self.fullscreen = False
        
        self.init_ui()
        #self.menu = Menu(self.file_list,self.current_index)
        
        
        
        
        #self.installEventFilter(self.menu)

    def init_ui(self):
        self.setWindowTitle('Image Viewer')
        self.setGeometry(300, 100, 800, 550)
        
        self.image_view = QGraphicsView(self)
        self.image_view.setAlignment(Qt.AlignCenter)
        self.image_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.image_view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        self.scene = QGraphicsScene()
        self.image_view.setScene(self.scene)
        
        self.menu = Menu(self.file_list, self.current_index, self.image_view)
        self.menu.copy_signal.connect(self.copyToClipboard)
        self.menu.delete_signal.connect(self.delete_image)
        self.menu.show_folder.connect(self.show_containing_folder)
        self.image_view.installEventFilter(self.menu)
        
        # this is to fix weird behaviour similar to stackoverflow Q #68182395
        QTimer.singleShot(0, self.handle_timeout)
        self.image_view.wheelEvent = self.zoom_image

        
        self.file_list = []
        self.setMouseTracking(True)
        self.load_images()

        # Main layout using QVBoxLayout
        layout = QVBoxLayout(self)
        Hlayout=QHBoxLayout()
        header_layout=QHBoxLayout()
        self.editing_buttons_layout = QHBoxLayout()

       
        self.leftBrowse = QPushButton( self)
        self.rightBrowse = QPushButton( self)
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
        self.scan_qrc_button=QPushButton()
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
        self.scan_qrc_button.setIcon(qta.icon('mdi6.qrcode-scan',color='white'))
        self.sharpen_button.setIcon(qta.icon('mdi.details',color='white'))
        self.set_exposure_button.setIcon(qta.icon('ei.adjust-alt',color='white'))
        self.flip_button.setIcon(qta.icon('mdi.reflect-horizontal',color='white'))
        self.compare_button.setIcon(qta.icon('mdi.select-compare',color='white'))
        self.leftBrowse.setIcon(qta.icon('fa.angle-left',color=self.config_data['background']))
        self.rightBrowse.setIcon(qta.icon('fa.angle-right',color=self.config_data['background']))

        
       
        #tooltip
        self.rotate_button.setToolTip('Rotate')
        self.undo_button.setToolTip('Undo')
        self.gray_button.setToolTip('Gray scale')
        self.gaussianBlur_button.setToolTip('Blur')
        self.blur_background_button.setToolTip('Portrait')
        self.flip_button.setToolTip('Right click to flip vertically')
        self.sharpen_button.setToolTip('Sharpen')
        self.set_exposure_button.setToolTip('adjust')
        self.show_containing_folder_button.setToolTip('Show containing folder')
        
        self.exposure_slider = QSlider(Qt.Horizontal)
        self.exposure_slider.setMinimum(2)
        self.exposure_slider.setMaximum(200)
        self.exposure_slider.setValue(100)  
        self.exposure_slider.valueChanged.connect(self.update_exposure)
        self.exposure_slider.hide()
        
        
        self.editing_buttons=[ self.scan_qrc_button ,self.set_exposure_button ,self.sharpen_button,self.gray_button,
                self.gaussianBlur_button,self.rotate_button,self.flip_button,
                 self.blur_background_button,self.compare_button, self.revert_button,self.undo_button,self.save_button
                ]
        navigation_buttons=[self.leftBrowse,self.rightBrowse ,self.back_button,self.show_containing_folder_button]
        
        #setting focus policy for all buttons
        for button in self.editing_buttons+navigation_buttons:
            button.setFocusPolicy(Qt.NoFocus)

        
        self.image_view.setFocusPolicy(Qt.NoFocus)
        #adding editing buttons to th editing buttons layout2+++++++
        for  button in self.editing_buttons:
            button.setFixedHeight(40)

            self.editing_buttons_layout.addWidget(button)
   
        layout.addLayout(header_layout)
        layout.addLayout(Hlayout)
        #layout.addWidget(self.exposure_slider)
        layout.addLayout(self.editing_buttons_layout)
        self.setLayout(layout)

        # Connect button signals to their respective functions
        
        self.sharpen_button.clicked.connect(self.sharpen_image)
        self.gray_button.clicked.connect(self.BGR2GRAY)
        self.gaussianBlur_button.clicked.connect(self.gaussianBlur)
        self.rotate_button.clicked.connect(self.rotateCCW)
        self.flip_button.clicked.connect(self.flipH)
        self.flip_button.setContextMenuPolicy(Qt.CustomContextMenu)
        self.flip_button.customContextMenuRequested.connect(self.flipV)
        self.rotate_button.setContextMenuPolicy(Qt.CustomContextMenu)
        self.rotate_button.customContextMenuRequested.connect(self.rotateCW)

        
        #self.set_exposure_button.clicked.connect(self.toggle_exposure_slider)
        self.set_exposure_button.clicked.connect(self.adjust)

        self.save_button.clicked.connect(self.save_image)
        self.back_button.clicked.connect(self.close)

        self.blur_background_button.clicked.connect(self.blurBackground)
        self.scan_qrc_button.clicked.connect(self.scanQRC)
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
        self.setStyleSheet(f"background-color: {self.config_data['background']};")
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
                "}}").format(border_color=border_color,icon_size=self.config_data['standard_icon_size'])

        
        
        for button in self.editing_buttons:
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
        
        self.back_button.setFixedSize(self.NAVBUTTONWIDTH,40) 
        self.show_containing_folder_button.setFixedSize(self.NAVBUTTONWIDTH,40)
        self.leftBrowse.setFixedSize(self.NAVBUTTONWIDTH, self.height())
        self.rightBrowse.setFixedSize(self.NAVBUTTONWIDTH, self.height())

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
            self.close()
        
        if event.key()==Qt.Key_Delete:
            self.delete_image()
            
        #saving edited images         
        if event.key()==Qt.Key_S :
            self.save_image()
            
        if event.key()==Qt.Key_F:
            self.toggleFullScreen()
        
        if event.key()==Qt.Key_C:
            self.copyToClipboard()
         
        if event.key()==Qt.Key_F1:
            help_page = 'https://mgama1.github.io/Ogallery/page/guide.html'
            webbrowser.open(help_page)
        
            
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggleFullScreen()
            
    def toggleFullScreen(self):
        self.toggleButtonsVisibility(self.editing_buttons)
        if not self.fullscreen:
            self.showFullScreen()
            if self.edit_history:
                QTimer.singleShot(100, self.show_edited_image)  # Delayed call to show_edited_image()
            else:
                QTimer.singleShot(100, self.show_image)  # Delayed call to show_image()

            self.fullscreen = True
        else:
            self.showNormal()
            if self.edit_history:
                QTimer.singleShot(100, self.show_edited_image)  # Delayed call to show_edited_image()
            else:
                QTimer.singleShot(100, self.show_image)  # Delayed call to show_image()
            self.fullscreen = False
    
    def toggleButtonsVisibility(self,buttons_list):
        for button in buttons_list:
            button.setVisible(self.fullscreen)
        
    def next_image(self):
        if hasattr(self, 'edited_image'):
            msg_box = SaveDiscardMessageBox(self.file_list[self.current_index],self.edited_image)
            msg_box.revert_signal.connect(self.revert)
            msg_box.exec_()
        
        self.current_index = (self.current_index + 1) % len(self.file_list)
        self.purge()
        self.show_image()

    def previous_image(self):
        if hasattr(self, 'edited_image'):
            msg_box = SaveDiscardMessageBox(self.file_list[self.current_index],self.edited_image)
            msg_box.revert_signal.connect(self.revert)
            msg_box.exec_()
            
        self.current_index = (self.current_index - 1) % len(self.file_list)
        self.purge()
        self.show_image()
        
    
    def set_transparency(self, alpha):
        self.rightBrowse.setStyleSheet(f"background-color: rgba(22,22,22,{alpha});border: none;color: rgba(255,255,255,{alpha});")
        self.leftBrowse.setStyleSheet(f"background-color: rgba(22,22,22,{alpha});border: none;color: rgba(255,255,255,{alpha});")
        if alpha==.5:
            self.leftBrowse.setIcon(qta.icon('fa.angle-left',color='white'))
            self.rightBrowse.setIcon(qta.icon('fa.angle-right',color='white'))
        if alpha==0:
            self.leftBrowse.setIcon(qta.icon('fa.angle-left',color=self.config_data['background']))
            self.rightBrowse.setIcon(qta.icon('fa.angle-right',color=self.config_data['background']))

    def on_enter_event(self, event):
        self.set_transparency(.5)

    def on_leave_event(self, event):
        self.set_transparency(0)
     

    def adjust(self):
        try:
            self.adjust_instance = Adjust(self)
            self.adjust_instance.show()
        except Exception as e:
            print(f"Error adjusting image: {e}")

        
        
    
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

    def rotateCW(self):
        if hasattr(self, 'edited_image'):
            img=self.edited_image
        else :
            image_path = self.file_list[self.current_index]
            img = cv2.imread(image_path)
        
        rotatedImg=cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
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

    def flipV(self):
        if hasattr(self, 'edited_image'):
            img=self.edited_image
        else :
            image_path = self.file_list[self.current_index]
            img = cv2.imread(image_path)
        
        flipped_img=cv2.flip(img, 0)
        self.edited_image=flipped_img
        self.edit_history.append(self.edited_image)
        self.show_edited_image()

    def change_contrast(self, contrast_factor):
        contrast_factor /= 100
            
        # Convert image to floating point representation
        img_float = self.colors_transformation_image.astype(np.float32) / 255.0
        
        # Apply contrast adjustment
        self.colors_transformation_image = (img_float - 0.5) * contrast_factor + 0.5
        
        # Clip values to range [0, 1]
        self.colors_transformation_image = np.clip(self.colors_transformation_image, 0, 1)
        
        # Convert back to uint8
        self.colors_transformation_image = (self.colors_transformation_image * 255).astype(np.uint8)
        
        
    def changeSaturation(self,offset_value):
        # Convert the image to HSV
        hsv_image = cv2.cvtColor(self.colors_transformation_image, cv2.COLOR_BGR2HSV)
        # Create a mask for pixels with high saturation
        saturation_mask = hsv_image[:, :, 1] > 10
        # Shift the hue channel by the specified value
        #hsv_image[:, :, 1] = np.clip(hsv_image[:, :, 1].astype(float) + offset_value, 0, 255).astype(np.uint8)
        hsv_image[:, :, 1] = np.where(saturation_mask, np.clip(hsv_image[:, :, 1].astype(int) + offset_value, 0, 255), hsv_image[:, :, 1]).astype(np.uint8)

        

        self.colors_transformation_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

    def changeHue(self,shift_value):        
        # Convert the image to HSV
        hsv_image = cv2.cvtColor(self.colors_transformation_image, cv2.COLOR_BGR2HSV)
    
        # Shift the hue channel by the specified value
        hsv_image[:, :, 0] = ((hsv_image[:, :, 0].astype(float) + shift_value)% 180).astype(np.uint8) 
    
        # Convert the image back to BGR
        self.colors_transformation_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

    
    def change_brightness(self,brightness_offset):       
        self.colors_transformation_image = cv2.add(self.colors_transformation_image, brightness_offset)
        
        
        
    def applyColorsTransformations(self,contrast_factor,brightness_offset,s_shift_value,shift_value):
        if self.edit_history:
            self.colors_transformation_image=self.edit_history[-1]
        else:   
            image_path = self.file_list[self.current_index]
            self.colors_transformation_image = cv2.imread(image_path)
                
        self.change_contrast(contrast_factor)
        self.change_brightness(brightness_offset)
        self.changeSaturation(s_shift_value)
        self.changeHue(shift_value)
        self.edited_image=self.colors_transformation_image
        #self.edit_history.append(self.edited_image)
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
    
    def scanQRC(self):
        decoded_list = decodeqr(Image.open(self.file_list[self.current_index]))
        self.qrcode_windows = []  # Create a list to store all the QRCodeWindow instances
        
        parent_rect = self.geometry()
        img_shape = cv2.imread(self.file_list[self.current_index]).shape
        scale_factor = self.image_view.transform().m11()
        
        for box in decoded_list:
            decoded = box[0]
            print(decoded)
            rpos_x, rpos_y = box.polygon[1]
            
            decoded_text = box.data.decode()
            if decoded_text:
                qrcode_window = QRCodeWindow(decoded_text)
                self.qrcode_windows.append(qrcode_window)  # Add the window to the list to keep a reference
                
                # Calculate the displayed dimensions
                displayed_width = img_shape[1] * scale_factor
                displayed_height = img_shape[0] * scale_factor  # Fixed the height calculation to use img_shape[0]
                
                # Get the bounding box of the QR code
                min_x = min(point.x for point in box.polygon)
                max_x = max(point.x for point in box.polygon)
                min_y = min(point.y for point in box.polygon)
                max_y = max(point.y for point in box.polygon)
                
                # Calculate the center of the QR code
                center_x = (min_x + max_x) / 2
                center_y = (min_y + max_y) / 2
                
                pos_x = int(parent_rect.left() + (parent_rect.width() - displayed_width) // 2 + (center_x * scale_factor) - 25)  # Center the text horizontally
                pos_y = int(parent_rect.top() + (parent_rect.height() - displayed_height) // 2 + (center_y * scale_factor) - 10)  # Center the text vertically
                print(displayed_width, displayed_height)
                
                qrcode_window.setGeometry(pos_x, pos_y, 50, 20)  # Adjust the size as needed
                qrcode_window.setStyleSheet("background-color: rgba(255, 255, 255, 0.5);")
                
                qrcode_window.show()


    def closeAllQRCodes(self):
        if hasattr(self,'qrcode_windows'):
            for window in self.qrcode_windows:
                window.close()
            self.qrcode_windows = []  

         
        
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
        self.edit_history=[]
        self.show_image()
    def purge(self):
        self.closeAllQRCodes()
        
    def save_image(self):
        if hasattr(self, 'edited_image'):
            msg_box = SavingMessageBox(self.file_list[self.current_index],self.edited_image)
            msg_box.exec_()
            delattr(self,'edited_image')
            self.edit_history=[]
            choice = msg_box.get_choice()
            file_name=msg_box.getFileName()
            saved={'index':self.current_index,'choice':choice,'file_name':file_name}
            time.sleep(.1)
            self.savedSignal.emit(saved)
            
        else:
            self.showErrorMessage("no changes were made!")
    
    def delete_image(self):
        file_name=self.file_list[self.current_index]
        if os.path.exists(file_name):
            
            try:
                os.system(f"gio trash '{self.file_list[self.current_index]}'")

            except OSError as e:
                print(f"Error moving file to trash: {e.filename} - {e.strerror}")
            
            deleted={'index':self.current_index,'file_name':self.file_list[self.current_index]}
            self.file_list.pop(self.current_index)
            self.show_image()
            
            time.sleep(.1)
            self.deletedSignal.emit(deleted)
            
            #db=pd.read_csv("db.csv")
            #if file_name in db["directory"].values:
            #    db=db[db["directory"]!=file_name]
             #   db.to_csv("db.csv")
            
            
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
        pixmap = QPixmap('media/angry.png').scaledToWidth(150)
        msg_box.setIconPixmap(pixmap)
        msg_box.setText(msg)
        msg_box.setWindowTitle('Warning')
        msg_box.exec_()
    
    

    def show_containing_folder(self):
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
                print(1)
                return True
            except subprocess.CalledProcessError:
                print(2)
                continue

        # If none of the commands were successful
        print(3)
        return False



    
    def closeEvent(self, event):
        # Override the closeEvent method to handle the window close event
        self.purge()
        self.finishedSignal.emit()
        event.accept()
        



class QRCodeWindow(QWidget):
    def __init__(self, decoded_text):
        super().__init__()
        self.setGeometry(0,0,15,15)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.qrtext_label = QLabel(self)
        # Set the text as a hyperlink
        self.qrtext_label.setText(f'<a href="{decoded_text}">{decoded_text}</a>')
        self.qrtext_label.setOpenExternalLinks(True)  # Open the link in a web browser
        self.qrtext_label.adjustSize()
        #self.qrtext_label.setGeometry(0, 0, self.width() // 2, self.qrtext_label.height())

        self.close_button = QPushButton("x", self)
        #self.close_button.setGeometry(self.width()-5,0, 20, 20)
        self.close_button.clicked.connect(self.close)
        self.qrtext_label.setMaximumWidth(200)
        self.close_button.setFixedSize(15,15)
        layout=QVBoxLayout()
        layout.addWidget(self.close_button)
        layout.addWidget(self.qrtext_label)
        self.setLayout(layout)




class InfoWidget(QWidget):
    def __init__(self):
        '''
        this info widget is only for app description and information not error messages and what not
        '''
        super().__init__()
        with open('config.yaml', 'r') as file:
            self.config_data = yaml.safe_load(file)
        self.setStyleSheet(f"background-color: {self.config_data['background']};color:white;"
                          )
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Info')
        self.setGeometry(500, 200, 400, 300)

        layout = QVBoxLayout()

        # Horizontal Layout for Image and Text
        horizontal_layout = QHBoxLayout()

        # Image Label
        image_label = QLabel(self)
        pixmap = QPixmap('media/info.png').scaledToWidth(150)
        image_label.setPixmap(pixmap)
        image_label.setMaximumWidth(150)
        horizontal_layout.addWidget(image_label)

        # Text Label
        info="""OGallery is an open‑source gallery app with advanced search capabilities, image viewing, and editing functionalities that aims to revolutinze user experience with images on Desktop """

        text_label = QLabel(self)
        text_label.setText(info)
        text_label.setMaximumWidth(300)
        text_label.setWordWrap(True)
        horizontal_layout.addWidget(text_label)

        layout.addLayout(horizontal_layout)

        # Footer Buttons
        footer_layout = QHBoxLayout()

        about_button = QPushButton('About', self)
        
        about_button.clicked.connect(lambda: text_label.setText(info))
        footer_layout.addWidget(about_button)

        authors_button = QPushButton('Authors', self)
        authors="""-Mahmoud Gamal"""
        authors_button.clicked.connect(lambda: text_label.setText(authors))
        footer_layout.addWidget(authors_button)

        website_button = QPushButton('Website', self)
        website_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl('https://mgama1.github.io/Ogallery/')))
        footer_layout.addWidget(website_button)
        footer_buttons=[about_button,authors_button,website_button]
        layout.addLayout(footer_layout)

        self.setLayout(layout)
        border_color='#242424'
        button_style = ("QPushButton {{"
                "background-color: #1f1f1f; "
                "color: white; "
                "icon-size:{icon_size};"
                "border:none"
                "}} "
                "QPushButton:hover {{"
                "background-color: #00347d; "
                "}}").format(border_color=border_color,icon_size=self.config_data['standard_icon_size'])
        for button in footer_buttons:
            button.setFixedHeight(50)
        for button in footer_buttons:
            button.setStyleSheet(button_style)


class Adjust(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.contrast_offset = 100
        self.saturation_offset=0
        self.hue_offset = 0
        self.brightness_offset = 0
        
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle('adjust')
        self.setGeometry(300, 100, 400, 400)
        self.setStyleSheet(f"background-color: #212121;color:'white';")
        self.contrast_label = QLabel('Contrast:', self)
        self.contrast_slider = QSlider(Qt.Horizontal)
        self.contrast_slider.setMinimum(30)
        self.contrast_slider.setMaximum(200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.valueChanged.connect(self.update_contrast_offset)
        self.contrast_value_label = QLabel(str(self.contrast_slider.value()), self)
        self.contrast_value_label.setText("1")
        
        self.brightness_label = QLabel('Brightness:', self)
        self.brightness_slider = QSlider(Qt.Horizontal)
        self.brightness_slider.setMinimum(-100)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.update_brightness_offset)
        self.brightness_value_label = QLabel(str(self.brightness_slider.value()), self)

        self.hue_label = QLabel('Hue:', self)
        self.hue_slider = QSlider(Qt.Horizontal)
        self.hue_slider.setMinimum(0)
        self.hue_slider.setMaximum(180)
        self.hue_slider.setValue(0)
        self.hue_slider.valueChanged.connect(self.update_hue_offset)
        self.hue_value_label = QLabel(str(self.hue_slider.value()), self)

        self.saturation_label = QLabel('saturation:', self)
        self.saturation_slider = QSlider(Qt.Horizontal)
        self.saturation_slider.setMinimum(-100)
        self.saturation_slider.setMaximum(100)
        self.saturation_slider.setValue(0)
        self.saturation_slider.valueChanged.connect(self.update_saturation_offset)
        self.saturation_value_label = QLabel(str(self.saturation_slider.value()), self)

        layout = QVBoxLayout(self)

        contrast_layout = QHBoxLayout()
        contrast_layout.addWidget(self.contrast_label)
        contrast_layout.addWidget(self.contrast_slider)
        contrast_layout.addWidget(self.contrast_value_label)

        brightness_layout = QHBoxLayout()
        brightness_layout.addWidget(self.brightness_label)
        brightness_layout.addWidget(self.brightness_slider)
        brightness_layout.addWidget(self.brightness_value_label)

        saturation_layout = QHBoxLayout()
        saturation_layout.addWidget(self.saturation_label)
        saturation_layout.addWidget(self.saturation_slider)
        saturation_layout.addWidget(self.saturation_value_label)
        
        hue_layout = QHBoxLayout()
        hue_layout.addWidget(self.hue_label)
        hue_layout.addWidget(self.hue_slider)
        hue_layout.addWidget(self.hue_value_label)

        self.reset_button=QPushButton('reset')
        self.reset_button.setFixedWidth(100)
        self.reset_button.clicked.connect(self.reset)
        layout.addWidget(self.reset_button,alignment=Qt.AlignRight)
        
        layout.addLayout(contrast_layout)
        layout.addLayout(brightness_layout)
        layout.addLayout(saturation_layout)
        layout.addLayout(hue_layout)
        

        self.setLayout(layout)

        self.contrast_slider.valueChanged.connect(self.update_contrast_value_label)
        self.brightness_slider.valueChanged.connect(self.update_brightness_value_label)
        self.saturation_slider.valueChanged.connect(self.update_saturation_value_label)
        self.hue_slider.valueChanged.connect(self.update_hue_value_label)

        self.contrast_slider.valueChanged.connect(self.applyAdjustments)
        self.brightness_slider.valueChanged.connect(self.applyAdjustments)
        self.saturation_slider.valueChanged.connect(self.applyAdjustments)
        self.hue_slider.valueChanged.connect(self.applyAdjustments)

    def applyAdjustments(self):
        self.parent().applyColorsTransformations(self.contrast_offset,self.brightness_offset,self.saturation_offset,self.hue_offset)
        
    def update_contrast_offset(self,contrast_val):
        self.contrast_offset = contrast_val

        
    def update_brightness_offset(self,brightness_val):
        self.brightness_offset = brightness_val

    def update_saturation_offset(self,saturation_val):
        self.saturation_offset = saturation_val
        
    def update_hue_offset(self,hue_val):
        self.hue_offset = hue_val

    
    def update_contrast_value_label(self, value):
        self.contrast_value_label.setText(str(value/100.0))

    def update_brightness_value_label(self, value):
        self.brightness_value_label.setText(str(value))


    def update_saturation_value_label(self, value):
        self.saturation_value_label.setText(str(value))
    def update_hue_value_label(self, value):
        self.hue_value_label.setText(str(value))

    def reset(self):
        self.contrast_offset = 100
        self.saturation_offset=0
        self.hue_offset = 0
        self.brightness_offset = 0
        
        self.contrast_slider.setValue(self.contrast_offset)
        self.brightness_slider.setValue(self.brightness_offset)
        self.hue_slider.setValue(self.hue_offset)
        self.saturation_slider.setValue(self.saturation_offset)
        
        
        

        
class CircularButton(QPushButton):
    def __init__(self, color, parent=None):
        super().__init__(parent)
        self.color=color
        self.setFixedSize(50, 50)
        self.setStyleSheet(f"background-color: {color}; border-radius: 25px;")
        self.clicked.connect(self.toggleBorder)

    def toggleBorder(self):
        self.parent().setStyleColor(self.color)
        self.parent().clearBorders()
        self.setStyleSheet(self.styleSheet() + "border: 2px solid white;")


class SettingsWidget(QWidget):
    colorChanged=pyqtSignal(str)
    def __init__(self):
        super().__init__()
        with open('config.yaml', 'r') as file:
            self.config_data = yaml.safe_load(file)
            
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Settings')
        self.setGeometry(300, 100, 800, 600)
        self.setStyleSheet(f"background-color: {self.config_data['background']};color:'white';")

        
        
       
        
        
        layout = QVBoxLayout(self)
        dir_layout=QHBoxLayout()
        dir_buttons_layout=QVBoxLayout()
        colors_layout = QHBoxLayout()
        
        colors = [
            "#ce3485",
            "#8c40d4",  
            "#2631c9",  
            "#5588db",  
            "#4bb7b5", 
            "#60b67d",  
            "#c86923" ,
            "#c41d21",
            "#212121",
        ]
        colors_layout.addStretch()
        self.colors_buttons = []
        for color in colors:
            button = CircularButton(color, self)
            colors_layout.addWidget(button)
            self.colors_buttons.append(button)
        colors_layout.addStretch()
        
        self.colors_buttons[-1].setStyleSheet("QPushButton {"
                     "border-image: url(media/batman.png);"
                     "border-radius: 25px;"
                     "}")
        self.model = QStringListModel()
        self.model.setStringList(self.getImagesPaths())

        self.listView = QListView()
        self.listView.setModel(self.model)
        dir_layout.addWidget(self.listView)

        # Add a button to remove directories
        self.remove_dir_button = QPushButton('Remove Directory')
        self.remove_dir_button.clicked.connect(self.removeSelectedItems)
        dir_buttons_layout.addWidget(self.remove_dir_button)

        self.add_dir_button = QPushButton('Add Directory')
        self.add_dir_button.clicked.connect(self.addItem)
        dir_buttons_layout.addWidget(self.add_dir_button)
        dir_buttons_layout.addStretch()
        dir_layout.addLayout(dir_buttons_layout)
        layout.addLayout(dir_layout)
        style_label = QLabel("style")
        layout.addWidget(style_label)
        layout.addSpacing(30)
        layout.addLayout(colors_layout)
        layout.addStretch()
        self.setLayout(layout)

    def setStyleColor(self,color):
        config_file_path = 'config.yaml'
        with open(config_file_path, 'r') as file:
            self.config_data = yaml.safe_load(file)
            
        self.config_data['style_color'] = color
        
        with open(config_file_path, 'w') as file:
            yaml.dump(self.config_data, file)
        self.colorChanged.emit(color)
    def clearBorders(self):
        for button in self.colors_buttons:
            button.setStyleSheet(button.styleSheet().replace("border: 2px solid white;", ""))
    
    def getImagesPaths(self):
        username = os.getenv('USER')
        if os.path.exists(f'/home/{username}/.cache/OpenGallery/config.log'):
            with open(f'/home/{username}/.cache/OpenGallery/config.log', 'r') as config_file:
                images_directories = config_file.readlines()
        elif not os.path.exists(f'/home/{username}/.cache/OpenGallery/'):
            os.makedirs(f'/home/{username}/.cache/OpenGallery/')
            with open(f'/home/{username}/.cache/OpenGallery/config.log', 'w') as config_file:
                config_file.write('\n')
        
        else:
            with open(f'/home/{username}/.cache/OpenGallery/config.log', 'w') as config_file:
                config_file.write('\n')

        return images_directories

    def addItem(self):
        self.showDialog()
        if self.selected_directory:
            self.model.insertRow(self.model.rowCount())
            index = self.model.index(self.model.rowCount() - 1)
            self.model.setData(index, self.selected_directory)

    def removeSelectedItems(self):
        indexes = self.listView.selectedIndexes()
        for index in sorted(indexes, reverse=True):
            # Get the data at the index with DisplayRole
            item_data = self.model.data(index, Qt.DisplayRole)
            self.model.removeRow(index.row())
            # Also remove from the config file
            username = os.getenv('USER')
            with open(f'/home/{username}/.cache/OpenGallery/config.log', 'r') as config_file:
                lines = config_file.readlines()
            with open(f'/home/{username}/.cache/OpenGallery/config.log', 'w') as config_file:
                for line in lines:
                    if line.strip() != item_data.strip():
                        config_file.write(line)


    def showDialog(self):
        username = os.getenv('USER')
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.selected_directory = QFileDialog.getExistingDirectory(self, "Select Directory", options=options)

        if self.selected_directory:
            if not os.path.exists(f'/home/{username}/.cache/OpenGallery/'):
                os.makedirs(f'/home/{username}/.cache/OpenGallery/')
            with open(f'/home/{username}/.cache/OpenGallery/config.log', 'a') as config_file:
                config_file.write(self.selected_directory + '\n')
   
    

    def keyPressEvent(self, event):    
        if (event.key() == Qt.Key_Backspace) or (event.key() == Qt.Key_Escape):
            self.close()
        
    
class Menu(QObject):
    copy_signal = pyqtSignal()
    delete_signal = pyqtSignal()
    show_folder = pyqtSignal()

    def __init__(self, file_list, current_index, graphics_view):
        super().__init__()
        self.opened_menu = None
        with open('config.yaml', 'r') as file:
            self.config_data = yaml.safe_load(file)
        self.file_list = file_list
        self.current_index = current_index
        self.graphics_view = graphics_view

    def eventFilter(self, obj, event):
        if obj is self.graphics_view and event.type() == QEvent.ContextMenu:
            if self.opened_menu is not None:
                self.opened_menu.close()
            menu = QMenu()
            copy_action = QAction("Copy", menu)
            copy_action.triggered.connect(self.copyToClipboardSignal)
            menu.addAction(copy_action)
            delete_action = QAction("Delete", menu)
            delete_action.triggered.connect(self.deleteSignal)
            menu.addAction(delete_action)
            show_folder_action = QAction("Show Containing Folder", menu)
            show_folder_action.triggered.connect(self.showContainingFolderSignal)
            menu.addAction(show_folder_action)

            self.opened_menu = menu
            menu.setStyleSheet(f"""
                QMenu {{
                    background-color: {self.config_data['background']};
                    color: white;
                }}
                QMenu::item:selected {{
                    background-color: {self.config_data['light_gray']};
                }}
            """)
            menu.exec_(QCursor.pos())
            return True
        return False

    def deleteSignal(self):
        self.delete_signal.emit()

    def copyToClipboardSignal(self):
        self.copy_signal.emit()

    def showContainingFolderSignal(self):
        self.show_folder.emit()


class ImageThumbnailWidget(QWidget):
    thumbnailClicked = pyqtSignal()
    viewerClosedSig = pyqtSignal()
    viewerSavedSig=pyqtSignal(dict)
    viewerDeletedSig=pyqtSignal(dict)
    selectedSig=pyqtSignal(int)
    def __init__(self, image_path, image_files,config_data):
        super().__init__()
        username = os.getenv('USER')
        self.cache_dir = f"/home/{username}/.cache/OpenGallery/"
        
        self.config_data=config_data
        self.image_path = image_path
        self.image_files = image_files
        self.right_clicked=False
        
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
            self.viewer = ImageViewer(self.image_files, current_index=self.image_files.index(self.image_path))
            self.viewer.finishedSignal.connect(self.viewerClosed)
            self.viewer.savedSignal.connect(self.viewerSaved)
            self.viewer.deletedSignal.connect(self.viewerDeleted)
            self.thumbnailClicked.emit()
    
        if event.button() == Qt.RightButton:
            
            if hasattr(self,'right_clicked'):
                self.right_clicked= not self.right_clicked
            else:
                self.right_clicked = True
            colors=[self.config_data['background'],'#3f5b63']
            self.setStyleSheet(f"background-color: {colors[self.right_clicked]};")
            #print(self.image_files.index(self.image_path))
            self.selectedSig.emit(self.image_files.index(self.image_path))
    

    
    def viewerClosed(self):
        self.viewerClosedSig.emit()
        
    def viewerSaved(self,saved):
        self.viewerSavedSig.emit(saved)
        
    def viewerDeleted(self,deleted):
        self.viewerDeletedSig.emit(deleted)
        
        
class ImageGalleryApp(QMainWindow):
    def __init__(self, image_files):
        super().__init__()
        with open('config.yaml', 'r') as file:
            self.config_data = yaml.safe_load(file)
            
        self.image_files = image_files
        self.thumbnail_widgets = []  # To store references to thumbnail widgets
        self.scroll_value =   0 # Initialize scroll_value
        self.initial_batch=12
        self.batch_size =   9  # Number of thumbnails to load per batch
        self.loaded_count =   0  
        self.scrollbar_threshold =   20  # Scrollbar threshold for loading thumbnails
        self.selected_indices=[]
        st=time.time()
        self.init_ui()
        et=time.time()
        print(f'loading time: {et-st}')
    
    def init_ui(self):
        central_widget = QWidget()
        self.setStyleSheet(f"background-color: {self.config_data['background']};")
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget(scroll_area)
        scroll_area.setWidget(scroll_content)
        self.layout = QGridLayout()
        scroll_content.setLayout(self.layout)
        
        row, col = 0, 0
        for index, image_file in enumerate(self.image_files):
            thumbnail_widget = ImageThumbnailWidget(image_file, self.image_files,self.config_data)
            #thumbnail_widget.thumbnailClicked.connect(self.hide)
            thumbnail_widget.viewerClosedSig.connect(self.showGallery)
            thumbnail_widget.viewerSavedSig.connect(self.getSavedData)
            thumbnail_widget.viewerDeletedSig.connect(self.getDeletedData)
            thumbnail_widget.selectedSig.connect(lambda selected_index:self.selected_indices.append(selected_index))
            self.layout.addWidget(thumbnail_widget, row, col)
            self.thumbnail_widgets.append(thumbnail_widget) 
            
            
            col += 1
            if col == 3:
                col = 0
                row += 1

        central_widget.setLayout(self.layout)
        scroll_area.setWidget(central_widget)
        self.setCentralWidget(scroll_area)
        
        self.scroll = scroll_area.verticalScrollBar()
        self.scroll.valueChanged.connect(self.update_thumbnails)
        

        self.setGeometry(300, 100, 800, 650)
        self.setWindowTitle('OGallery')
        self.show()
        self.load_initial_batch()#
        
    def load_initial_batch(self):
        for i in range(min(self.initial_batch,len(self.thumbnail_widgets))):
            self.thumbnail_widgets[self.loaded_count].load_thumbnail()
            self.loaded_count += 1

    def update_thumbnails(self):
        self.scroll_value = self.scroll.value()
        if self.scroll_value >= self.scrollbar_threshold:
            for i in range(min(len(self.thumbnail_widgets), self.batch_size)):
                if self.loaded_count < len(self.image_files):  # Load only if there's more to load
                    self.thumbnail_widgets[self.loaded_count].load_thumbnail()
                    self.loaded_count += 1
            self.scrollbar_threshold += 20  # Adjust the threshold by a fixed amount

            
    def showGallery(self):
        self.show()
        if hasattr(self,'savedData'):
            self.updateThumbnail(self.savedData)
            delattr(self,'savedData')
            
       
    def getSavedData(self, saved):
        self.savedData=saved
        
    def getDeletedData(self, deleted):
        print(deleted)
        self.removeThumbnail(deleted["index"])
        
    

        
    def updateThumbnail(self, saved):
        self.edited_index=saved["index"]
        choice=saved["choice"]
        file_name=saved["file_name"]
        
        if self.edited_index >= len(self.thumbnail_widgets):
            return
        if choice=='overwrite':
            thumbnail_widget = self.thumbnail_widgets.pop(self.edited_index)
            self.layout.removeWidget(thumbnail_widget)
            thumbnail_widget.deleteLater()  
            #reload the thumbnail widget from disk
            nthumbnail_widget = ImageThumbnailWidget(self.image_files[self.edited_index], self.image_files,self.config_data)
            nthumbnail_widget.load_thumbnail()
            nthumbnail_widget.thumbnailClicked.connect(self.hide)
            nthumbnail_widget.viewerClosedSig.connect(self.showGallery)
            nthumbnail_widget.viewerSavedSig.connect(self.getSavedData)
            nthumbnail_widget.selectedSig.connect(lambda selected_index:self.selected_indices.append(selected_index))
        if choice=='copy':
            #reload the thumbnail widget from disk
            nthumbnail_widget = ImageThumbnailWidget(file_name, self.image_files,self.config_data)
            nthumbnail_widget.load_thumbnail()
            self.image_files.insert(self.edited_index,file_name)
            nthumbnail_widget.thumbnailClicked.connect(self.hide)
            nthumbnail_widget.viewerClosedSig.connect(self.showGallery)
            nthumbnail_widget.viewerSavedSig.connect(self.getSavedData)
            nthumbnail_widget.selectedSig.connect(lambda selected_index:self.selected_indices.append(selected_index))
        else:
            pass
        
        self.thumbnail_widgets.insert(self.edited_index, nthumbnail_widget)
        self.loaded_count =   0  
        row, col = 0, 0
        for i, widget in enumerate(self.thumbnail_widgets):
            self.layout.addWidget(widget, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1



    def removeThumbnail(self, thumbnail_index):
        # Sort indices in reverse order to avoid index shifting issues
        thumbnail_widget = self.thumbnail_widgets.pop(thumbnail_index)
        #self.image_files.pop(thumbnail_index)
        self.layout.removeWidget(thumbnail_widget)
        thumbnail_widget.deleteLater()  # Delete the widget to free up resources

        # Clear the layout
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
    
        # Re-add remaining thumbnails to the layout
        row, col = 0, 0
        for i, widget in enumerate(self.thumbnail_widgets):
            self.layout.addWidget(widget, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1
    
        
    def getIndicesToDelete(self):
        '''
        gets indices to delete which are only the odd numbers of indices recieved. as even counts means that
        it was selected and unselected
        Args:
            None
        returns:
            indices to delete(list)
        '''
        count = {}
        indices_to_delete = []
        for e in self.selected_indices:
            count[e] = count.get(e, 0) + 1
            
        for e in count:
            if count[e] % 2 != 0:
                indices_to_delete.append(e)
        self.selected_indices = []
        return indices_to_delete
    def removeThumbnails(self, thumbnails_indices_list):
        # Sort indices in reverse order to avoid index shifting issues
        thumbnails_indices_list.sort(reverse=True)
        for thumbnail_index in thumbnails_indices_list:
            thumbnail_widget = self.thumbnail_widgets.pop(thumbnail_index)
            os.system(f"gio trash '{self.image_files[thumbnail_index]}'")
            self.image_files.pop(thumbnail_index)
            self.layout.removeWidget(thumbnail_widget)
            thumbnail_widget.deleteLater()  # Delete the widget to free up resources
    
        # Clear the layout
        for i in reversed(range(self.layout.count())):
            self.layout.itemAt(i).widget().setParent(None)
    
        # Re-add remaining thumbnails to the layout
        row, col = 0, 0
        for i, widget in enumerate(self.thumbnail_widgets):
            self.layout.addWidget(widget, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1
    
        

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Escape:
            self.close()        
        if event.key() == Qt.Key_M:
            print(self.selected_indices)

        if event.key() == Qt.Key_Delete:
            self.removeThumbnails(self.getIndicesToDelete())
            
        
            
def run_gui():
    app = QApplication([])    
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #000000; border: 1px solid white; }")  
    main_widget = MainWidget()
    app.exec_()

    
def run_inference_model():
    model=Model()
    model.predictAndSave()
    

                
if __name__ == '__main__':
    gui_process = multiprocessing.Process(target=run_gui)
    inference_process = multiprocessing.Process(target=run_inference_model)

    
    gui_process.start()
    inference_process.start()

    gui_process.join()
    inference_process.join()
    
