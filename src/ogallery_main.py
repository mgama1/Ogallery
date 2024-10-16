import time
import os
import sys
s=time.time()
os.environ['QT_API'] = 'pyqt5'
import threading
import yaml
from pyzbar.pyzbar import decode as decodeqr
import multiprocessing
import gc
import subprocess

from PIL import Image
from PyQt5.QtGui import QPixmap,QImage,QIcon,QCursor,QDesktopServices,QColor,QPainterPath,QPen,QFont,QBrush,QTransform
from PyQt5.QtCore import Qt,pyqtSignal,QTimer,QStringListModel,QObject,QEvent,QUrl,QRectF,QPointF
from PyQt5.QtCore import pyqtSlot

from PyQt5.QtWidgets import *


import qtawesome as qta

from itertools import chain



#os.environ['QT_QPA_PLATFORM'] = 'wayland'
#os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = '/path/to/your/qt/plugins'

from gallery.imageGallery import ImageGalleryApp
from gallery.imageThumbnail import ImageThumbnailWidget
from custom import *
from core.core import *
from core.vault import SecureFolder


def get_config_path(config_filename):
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        basedir = sys._MEIPASS
        config_path = os.path.join(basedir, 'config', config_filename)
    else:
        # Running in a normal Python environment
        basedir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(basedir, 'config', config_filename)
    
    if os.path.exists(config_path):
        return config_path
    
    # If not found, raise an error
    raise FileNotFoundError(f"Config file not found at {config_path}")
def get_media_path(media_filename):
    if getattr(sys, 'frozen', False):
        # Running in a PyInstaller bundle
        basedir = sys._MEIPASS
        config_path = os.path.join(basedir, 'media', media_filename)
    else:
        # Running in a normal Python environment
        basedir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(basedir, 'media',  media_filename)
    
    if os.path.exists(config_path):
        return config_path
    
    # If not found, raise an error
    raise FileNotFoundError(f"Config file not found at {config_path}")

#basedir = os.path.dirname(__file__)
print(time.time()-s)



class MainWidget(QWidget):
    def __init__(self):
        super().__init__()

        with open(get_config_path('config.yaml'), 'r') as file:
            self.config_data = yaml.safe_load(file)

        
        self.init_ui()
        self.import_data_in_background()
    def import_data_in_background(self):
        thread = threading.Thread(target=self.import_libraries)
        thread.start()

    def import_libraries(self):
        global np, pd, cv2,lev_distance
        import numpy as np
        import pandas as pd
        import cv2
        from Levenshtein import distance as lev_distance
        


    

    
    def init_ui(self):
        self.setWindowTitle('OGallery')
        self.setGeometry(300, 100, 750, 500)

        
        
        with open(get_config_path('classes_synonyms.yaml'), 'r') as file:
            classes_synonyms = yaml.safe_load(file)
        # Flatten keys and values of model.classes_synonyms
        self.classes_plus = chain(classes_synonyms.keys(), classes_synonyms.values())
        # Split, strip, and filter empty strings.
        self.classes_plus = [item.strip().replace("q_",'') for cls in self.classes_plus for item in cls.split(',') if item.strip()] 
        

        self.setWindowIcon(QIcon(get_media_path('iconc.ico')))

        if not os.path.exists(f"/home/{os.getenv('USER')}/.config/OpenGallery/"):
            os.makedirs(f"/home/{os.getenv('USER')}/.config/OpenGallery/")

        config_file_path = get_config_path('config.yaml')
        dynamic_config_path=f"/home/{os.getenv('USER')}/.config/OpenGallery/config.yaml"
        
        
        if not os.path.exists(dynamic_config_path):
            with open(dynamic_config_path, 'w') as file:
                style_color = {'style_color': '#8c40d4'}
                yaml.dump(style_color, file)
        
        with open(dynamic_config_path, 'r') as file:
            self.dynamic_config_data = yaml.safe_load(file)

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
        self.search_button.setIconHover(qta.icon('fa.search',color=self.dynamic_config_data["style_color"],scale_factor=1.1))
        
        self.info_button.setIconNormal(qta.icon('ei.info-circle',color=self.config_data['foreground']))
        self.info_button.setIconHover(qta.icon('ei.info-circle',color=self.dynamic_config_data["style_color"]))
        
        
        self.settings_button.setIconNormal(qta.icon('fa.cog',color=self.config_data['foreground']))
        self.settings_button.setIconHover(qta.icon('fa.cogs',color=self.dynamic_config_data["style_color"]))
        
        self.gallery_button.setIconNormal(qta.icon('mdi.folder-image',color=self.config_data['foreground']))
        self.gallery_button.setIconHover(qta.icon('mdi.folder-image',color=self.dynamic_config_data["style_color"]))
     
        self.show()


    def loadBackground(self):
        
        
        color=self.dynamic_config_data["style_color"]
        pixmap = QPixmap(get_media_path(f'{color}.png'))
        
            
        self.background_label = QLabel(self)
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True) 
        self.background_label.setGeometry(0, 0, self.width(), self.height())

    def updateBackground(self,color):
        pixmap = QPixmap(get_media_path(f'{color}.png'))
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
                self.images=self.result
                self.image_gallery=ImageGalleryApp(self)
                self.image_gallery.show()
                
    def openGallery(self):
        images_model=ImagesModel()
        self.images=images_model.getImagesPaths()
        if self.images:
            self.image_gallery=ImageGalleryApp(self)
            self.image_gallery.show()
    
        else:
            self.showErrorMessage("please setup the images directories")
    def openViewer(self,image_path,secure_mode):
        
        
        ImageViewer(self,image_path,secure_mode=secure_mode)

    def imageViewerDeleted(self,index):
        self.image_gallery.removeThumbnail(index)
    
    def imageViewerSaved(self,saved_dic):
        self.image_gallery.updateThumbnail(saved_dic)
    
    def openLockedFolderGallery(self,decrypted_files,password):
        self.image_gallery.close()
        
        self.images=decrypted_files
        self.image_gallery=ImageGalleryApp(self,secure_mode=True)
        #you have to connect before showing
        self.image_gallery.finishedSignal.connect(lambda:SecureFolder().closeLockedFolder(self.images,password))
        self.showMinimized()
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
        
    


    def selectImages(self):
        self.queryText=self.query_line.text()
        if self.queryText=='':
                    self.showErrorMessage("Forgetting something?")
                    return 0
        self.queryText=self.suggestClasses(self.queryText)
        self.result=[]
        
        try:
            config_path=f"/home/{os.getenv('USER')}/.config/OpenGallery/"
   
            db=pd.read_csv(f"{config_path}db.csv")
            self.filtered_classes=db[db["class"].str.contains("q_"+self.queryText) | db["synonyms"].str.contains("q_"+self.queryText) ]["directory"].to_list()
            #Not every file in the csv still exists. some are deleted; whether from ogallery or externally
            #instead of continously checking and updating. we only check and update upon search
            for filePath in self.filtered_classes:
                if os.path.exists(filePath):
                    self.result.append(filePath)
        except:
            print("no csv for now")
        # file names pattern matching
        images_model=ImagesModel()
        for images_dir in images_model.images_directories:
            filename_matches=self.searchFileNames(images_dir,self.queryText,images_model.file_types)
            self.result.extend(filename_matches)
        
        self.result.sort(key=lambda x: os.path.getmtime(x),reverse=True)

        if len(self.result)<1:
            self.showErrorMessage("no matches found!")
            return 0
        return 1
    
    

    def searchFileNames(self, parent_dir, search_string,file_types):
        """
        Searches for files in a parent directory recursively, matching file names containing a search string
        and filtering by specific file extensions.
        
        Args:
            parent_dir (str): The directory to search in.
            search_string (str): The string to search for in file names.
            
        Returns:
            list: A list of matched file paths.
        """
        #todo:move this to image model
        matched_files = []
        search_string = search_string.lower()  

        for root, dirs, files in os.walk(parent_dir):
            for file in files:
                # Check if file matches the search string and has a valid extension
                if search_string in file.lower():
                    file_extension = file.split('.')[-1].lower()  # Get the file extension and convert to lowercase
                    if file_extension in file_types:  # Only match specified file types
                        file_path = os.path.join(root, file)
                        #to avoid duplication in the case that an image has a substring the same as the class
                        if file_path not in self.result:
                            matched_files.append(file_path)
        
        return matched_files

    
        
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
        
        #No matches found.
        return query
    
    
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
        pixmap = QPixmap(get_media_path('warning.png')).scaledToWidth(150)
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
    def __init__(self,main_widget,image_path,secure_mode=False):
        super().__init__()
        self.secure_mode=secure_mode
        self.main_widget = main_widget  
        self.NAVBUTTONWIDTH=60
        with open(get_config_path('config.yaml'), 'r') as file:
            self.config_data = yaml.safe_load(file)
        self.current_index = main_widget.images.index(image_path)
        self.image_files = self.main_widget.images
        
        self.edit_history=CircularBuffer(10)
        self.fullscreen = False
        self.slideshow=False
        self.edited_image=None
        self.init_ui()
        

    def init_ui(self):
        self.setupWindow()
        self.setupGraphicsView()
        self.setupMenu()
        self.setupButtons()
        self.setupLayout()
        self.setStyles()
        self.setupHoverEvents()
        
        self.set_transparency(0)
        self.show_image()
        self.show()
      
    def setupWindow(self):
        self.setWindowTitle('Ogallery')
        self.setGeometry(300, 100, 800, 650)

        
    def setupGraphicsView(self):
        self.image_view = PanningGraphicsView(self)
        self.scene = QGraphicsScene()
        self.image_view.setScene(self.scene)
        self.image_view.setFocusPolicy(Qt.NoFocus)
        QTimer.singleShot(0, self.handle_timeout)

    def setupMenu(self):
        self.menu = Menu(self.image_view)
        self.menu.copy_signal.connect(self.copyToClipboard)
        self.menu.delete_signal.connect(self.delete_image)
        self.menu.show_folder.connect(self.show_containing_folder)
        self.image_view.installEventFilter(self.menu)


    def create_button(self, icon_name=None, tooltip_text='', callback=None, parent=None,text=None,sf=1):
        button = QPushButton(parent)
        if icon_name:
            button.setIcon(qta.icon(icon_name, color='white',scale_factor=sf))
        else:
            button.setText(text)
        button.setToolTip(tooltip_text)
        if callback:
            button.clicked.connect(callback)
        button.setFixedHeight(40)
        button.setFocusPolicy(Qt.NoFocus)
        return button

    def setupButtons(self):
        
        self.leftBrowse = self.create_button('fa.angle-left', '', self.previous_image, parent=self)
        self.rightBrowse = self.create_button('fa.angle-right', '', self.next_image, parent=self)
        self.back_button = self.create_button(None, '', self.close, parent=self,text='↩')
        
        self.options_button = self.create_button('mdi.dots-vertical', 'options', self.showOptionsMenu, parent=self,sf=1.6)
        self.gray_button = self.create_button('mdi.image-filter-black-white', 'Gray scale', self.BGR2GRAY, parent=self)
        self.rotate_button = self.create_button('mdi6.rotate-left', 'Rotate', self.rotateCCW)
        self.crop_button=self.create_button('mdi.crop', 'crop', self.add_crop_rect, parent=self)

        self.flip_button = self.create_button('mdi.reflect-horizontal', 'Right click to flip vertically', self.flipH, parent=self)
        self.adjust_button = self.create_button('ei.adjust-alt', 'Adjust', self.adjust, parent=self)
        self.blur_background_button = self.create_button('fa.user', 'Portrait', self.blurBackground, parent=self)
        self.scan_qrc_button = self.create_button('mdi6.qrcode-scan', '', self.scanQRC, parent=self)
        self.undo_button = self.create_button('mdi.undo-variant', 'Undo', self.undo, parent=self)
        self.compare_button = self.create_button('mdi.select-compare', '', None, parent=self)
        self.compare_button.pressed.connect(self.show_image)
        self.compare_button.released.connect(self.show_edited_image)
        self.revert_button = self.create_button(None, 'Revert', self.revert, parent=self,text='revert')
        self.save_button = self.create_button('fa5.save', '', self.save_image, parent=self)
        self.flip_button.setContextMenuPolicy(Qt.CustomContextMenu)
        self.flip_button.customContextMenuRequested.connect(self.flipV)
        self.rotate_button.setContextMenuPolicy(Qt.CustomContextMenu)
        self.rotate_button.customContextMenuRequested.connect(self.rotateCW)

        self.editing_buttons=[ self.scan_qrc_button ,self.adjust_button ,self.gray_button,
                self.rotate_button,self.crop_button,self.flip_button,
                 self.blur_background_button,self.compare_button, self.revert_button,self.undo_button,self.save_button
                ]
        self.navigsetupLayoutation_buttons=[self.leftBrowse,self.rightBrowse ,self.back_button,self.options_button]


    def add_crop_rect(self):
            self.crop_rect = CornerBasedRectItem(0, 0, self.image_width, self.image_height, self.image_width, self.image_height)
            self.scene.addItem(self.crop_rect)
            self.rightBrowse.setVisible(False)
            self.leftBrowse.setVisible(False)
            
    def applyCrop(self):
        if hasattr(self, 'crop_rect'):
                coords = self.crop_rect.get_relative_coordinates()
                #print(f"Rectangle coordinates: x={coords['x']}, y={coords['y']}, "
                #      f"width={coords['width']}, height={coords['height']}")
                if self.edited_image is not None:
                    img=self.edited_image
                else :
                    image_path = self.image_files[self.current_index]
                    img = cv2.imread(image_path)
                x=coords['x']
                y=coords['y']
                cropped_image = img[y:y+coords['height'], x:x+coords['width']]
                
                self.edited_image=cropped_image
                self.edit_history.add(self.edited_image)
                self.show_edited_image()
                #clean up
                self.rightBrowse.setVisible(True)
                self.leftBrowse.setVisible(True)
                delattr(self,"crop_rect")
    
    def setupLayout(self):
        layout = QVBoxLayout(self)
        self.Hlayout = QHBoxLayout()
        header_layout = QHBoxLayout()
        self.editing_buttons_layout = QHBoxLayout()

        self.Hlayout.addWidget(self.image_view)
        
        header_layout.addWidget(self.back_button)
        header_layout.addStretch(1)
        header_layout.addWidget(self.options_button)

        for button in self.editing_buttons:
            button.setFixedHeight(40)
            self.editing_buttons_layout.addWidget(button)

        layout.addLayout(header_layout)
        layout.addLayout(self.Hlayout)

        layout.addLayout(self.editing_buttons_layout)
        
        if self.secure_mode:
            for button in self.editing_buttons:
                button.setVisible(False)
        # Set absolute positions for leftBrowse and rightBrowse
        self.leftBrowse.setParent(self)
        self.leftBrowse.setGeometry(10, self.height() // 2 - self.leftBrowse.height() // 2, self.leftBrowse.width(), self.leftBrowse.height())

        self.rightBrowse.setParent(self)
        self.rightBrowse.setGeometry(self.width() - self.rightBrowse.width() - 10, self.height() // 2 - self.rightBrowse.height() // 2, self.rightBrowse.width(), self.rightBrowse.height())

        self.setLayout(layout)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.leftBrowse.setFixedSize(self.NAVBUTTONWIDTH, int(self.height()/1.25))
        self.rightBrowse.setFixedSize(self.NAVBUTTONWIDTH, int(self.height()/1.25))
        # Reposition leftBrowse and rightBrowse on window resize
        self.leftBrowse.move(10, self.height() // 2 - self.leftBrowse.height() // 2)
        self.rightBrowse.move(self.width() - self.rightBrowse.width() - 10, self.height() // 2 - self.rightBrowse.height() // 2)
        



    def setStyles(self):
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
        
        
        
        header_button_style=(
            "QPushButton {background-color: rgba(22, 22, 22, 0); \
            border: none; \
            color: white; \
            font-size: 16pt;} \
            QPushButton:hover {background-color: #2e2e2e;} "
        )

        options_button_style=(
            "QPushButton {background-color: rgba(22, 22, 22, 0); \
            border: none; \
            color: white; \
            font-size: 32pt;} \
            QPushButton:hover {background-color: #2e2e2e;} "
        )
        self.back_button.setStyleSheet(header_button_style)
        self.options_button.setStyleSheet(options_button_style)
        
        self.back_button.setFixedSize(self.NAVBUTTONWIDTH,40) 
        self.options_button.setFixedSize(self.NAVBUTTONWIDTH//2,40)
        self.leftBrowse.setFixedSize(self.NAVBUTTONWIDTH, int(self.height()/1.25))
        self.rightBrowse.setFixedSize(self.NAVBUTTONWIDTH, int(self.height()/1.25))

        browsing_buttons_style= "background-color: rgba(22, 22, 22, .5); \
                                                    color: white; \
                                                    border: none;"
        self.leftBrowse.setStyleSheet(browsing_buttons_style)
        self.rightBrowse.setStyleSheet(browsing_buttons_style)

        self.image_view.setStyleSheet("border: none;")
    

    def setupHoverEvents(self):
        self.rightBrowse.enterEvent = self.on_enter_event
        self.rightBrowse.leaveEvent = self.on_leave_event
        self.leftBrowse.enterEvent = self.on_enter_event
        self.leftBrowse.leaveEvent = self.on_leave_event
        
    def show_image(self):
        if self.image_files:
            image_path = self.image_files[self.current_index]
            pixmap = QPixmap(image_path)
            image_size = pixmap.size()
            self.image_width = image_size.width()
            self.image_height = image_size.height()
            self.scene.clear()
            self.pixmap_item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(self.pixmap_item)
            self.scene.setSceneRect(self.pixmap_item.boundingRect())
            self.image_view.fitInView(self.pixmap_item, Qt.KeepAspectRatio)
            self.setWindowTitle(os.path.splitext(os.path.basename(image_path))[0])
        else:
            self.close()
    def show_edited_image(self):
        try:
            self.scene.clear()
            pixmap = QPixmap(self.convert_cv_image_to_qpixmap(self.edited_image))
            image_size = pixmap.size()
            self.image_width = image_size.width()
            self.image_height = image_size.height()
            self.pixmap_item = QGraphicsPixmapItem(pixmap)
            self.scene.addItem(self.pixmap_item)
            self.scene.setSceneRect(self.pixmap_item.boundingRect())
            self.image_view.fitInView(self.pixmap_item, Qt.KeepAspectRatio)
        except:
            self.show_image()

    def startSlideShow(self):
        if not self.slideshow:
            self.slideshow=True
            if not self.fullscreen:
                self.toggleFullScreen()
            self.ss_timer = QTimer(self)
            self.ss_timer.timeout.connect(self.next_image)
            self.ss_timer.start(3000)

    def stopSlideShow(self):
        if self.slideshow:
            self.ss_timer.stop()
            self.slideshow=False
            if self.fullscreen:
                self.toggleFullScreen()

    def handle_timeout(self):
        if self.image_files:
            image_path = self.image_files[self.current_index]
            pixmap = QPixmap(image_path)
            pixmap_item = QGraphicsPixmapItem(pixmap)

            self.image_view.fitInView(pixmap_item, Qt.KeepAspectRatio)
        
    def zoom_image(self, event):
        factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.image_view.scale(factor, factor)

    def start_pan(self, event):
        if event.button() == Qt.LeftButton and not self.scene.itemAt(self.image_view.mapToScene(event.pos()), QTransform()):
            self.panning = True
            self.pan_start_pos = event.pos()
            self.image_view.viewport().setCursor(QCursor(Qt.ClosedHandCursor))
            return True
        return False

    def pan_image(self, event):
        if self.panning and self.pan_start_pos:
            delta = event.pos() - self.pan_start_pos
            self.image_view.horizontalScrollBar().setValue(
                self.image_view.horizontalScrollBar().value() - delta.x())
            self.image_view.verticalScrollBar().setValue(
                self.image_view.verticalScrollBar().value() - delta.y())
            self.pan_start_pos = event.pos()
            return True
        return False

    def stop_pan(self, event):
        if event.button() == Qt.LeftButton and self.panning:
            self.panning = False
            self.pan_start_pos = None
            self.image_view.viewport().setCursor(QCursor(Qt.ArrowCursor))
            return True
        return False


    def keyPressEvent(self, event):
        
        
        if event.key() == Qt.Key_Right:
            self.next_image()
        if event.key() == Qt.Key_Left:
            self.previous_image()
    
        if (event.key() == Qt.Key_Backspace) or (event.key() == Qt.Key_Escape):
            if self.fullscreen:
                self.toggleFullScreen()
                self.stopSlideShow()
            else:
                self.close()
        
        if event.key()==Qt.Key_Delete:
            self.delete_image()
            
        if event.key()==Qt.Key_S :
            self.save_image()
            
        if (event.key()==Qt.Key_F) or (event.key()==Qt.Key_F11):
            self.toggleFullScreen()
            self.stopSlideShow()
        if event.key()==Qt.Key_C:
            self.copyToClipboard()

        if event.key()==Qt.Key_I:
            self.showImageInfo()

        if event.key()==Qt.Key_Z:
            self.undo()
            
        if event.key()==Qt.Key_F1:
            help_page = 'https://ogalleryapp.github.io/page/guide.html'
            QDesktopServices.openUrl(QUrl(help_page))
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.applyCrop()
        if event.key()==Qt.Key_D:
            self.startSlideShow()
        if event.key()!=Qt.Key_D:
            self.stopSlideShow()
        
        super().keyPressEvent(event)
    
    

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.toggleFullScreen()
            self.stopSlideShow()
            
    def toggleFullScreen(self):
        self.toggleButtonsVisibility(self.editing_buttons)
        if not self.fullscreen:
            self.showFullScreen()
            if self.edited_image is not None:
                QTimer.singleShot(100, self.show_edited_image)  
            else:
                QTimer.singleShot(100, self.show_image)  
            self.fullscreen = True
        else:
            self.showNormal()
            if self.edited_image is not None:
                QTimer.singleShot(100, self.show_edited_image)  
            else:
                QTimer.singleShot(100, self.show_image)  
            self.fullscreen = False
    
    def toggleButtonsVisibility(self,buttons_list):
        for button in buttons_list:
            if not self.secure_mode:
                button.setVisible(self.fullscreen)
        self.back_button.setVisible(self.fullscreen)
        self.options_button.setVisible(self.fullscreen)
        
    def next_image(self):
        if not self.checkZeroDisplacement():
            msg_box = SaveDiscardMessageBox(self.image_files[self.current_index],self.edited_image)
            msg_box.revert_signal.connect(self.revert)
            msg_box.exec_()
            if msg_box.get_choice()=='save':
                self.save_image()
        self.purge()        
        self.current_index = (self.current_index + 1) % len(self.image_files)
        self.show_image()

    def previous_image(self):
        if not self.checkZeroDisplacement():
            msg_box = SaveDiscardMessageBox(self.image_files[self.current_index],self.edited_image)
            msg_box.revert_signal.connect(self.revert)
            msg_box.exec_()
            if msg_box.get_choice()=='save':
                self.save_image()
        self.purge()        
        self.current_index = (self.current_index - 1) % len(self.image_files)
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
            self.adjust_instance.exec_()
        except Exception as e:
            print(f"Error adjusting image: {e}")

        
        
    
    def copyToClipboard(self):
        image_path = self.image_files[self.current_index]
        clipboard = QApplication.clipboard()
        clipboard.setPixmap(QPixmap(image_path))
        
    def showImageInfo(self):
        img_path=self.image_files[self.current_index]
        file_size=self.format_file_size(os.path.getsize(img_path))
        type = (os.path.splitext(img_path)[-1][1:]).upper()
        msg_box = InfoMessageBox()
        pixmap = QPixmap(get_media_path('info.png')).scaledToWidth(150)
        msg_box.setIconPixmap(pixmap)
        msg=f"size: {self.image_width}x{self.image_height} pixels \nfile size: {file_size}\ntype: {type}"
        msg_box.setText(msg)
        msg_box.setWindowTitle('Image details')
        msg_box.exec_()
        
    def format_file_size(self,size_in_bytes):
        '''
        Convert the file size to KB, MB, or GB depending on its size
        '''
        if size_in_bytes < 1024:
            return f"{size_in_bytes} bytes"
        elif size_in_bytes < 1024 ** 2:
            return f"{size_in_bytes / 1024:.2f} KB"
        elif size_in_bytes < 1024 ** 3:
            return f"{size_in_bytes / (1024 ** 2):.2f} MB"
        else:
            return f"{size_in_bytes / (1024 ** 3):.2f} GB"
            
    
    def showOptionsMenu(self):
        menu = QMenu(self)
        if self.secure_mode:
            menu.addAction("Move out of locked folder",self.removeFromLockedFolder)
        else:
            menu.addAction("Move to locked folder",self.addToLockedFolder)
            menu.addAction("Image details",self.showImageInfo)
            menu.addAction("Open Locked folder",self.openLockedFolder)
        menu.setStyleSheet("""
            QMenu {
                background-color: #212121; 
            }
            QMenu::item {
                color: #ffffff;
                background-color: transparent;  /* Background color of each item */
            }
            QMenu::item:selected {
                background-color: #2e2e2e;  /* Background color when hovering over an item */
                color: #ffffff;  /* Text color when hovering */
            }
        """)
        # Show the menu at the button's position
        menu.exec_(self.options_button.mapToGlobal(self.options_button.rect().bottomLeft()))
   
    def addToLockedFolder(self):
        self.secure_folder=SecureFolder()
        
        if self.secure_folder.hasExistingPassword():
            password=self.requestPassword()
            if password is None:
                return 0
            if self.secure_folder.encrypt(self.image_files[self.current_index],password):
                self.image_files.pop(self.current_index)
                self.main_widget.imageViewerDeleted(self.current_index)
                self.show_image()
            else:
                self.showErrorMessage("Password is incorrect!")
        else:
            password=self.requestNewPassword()
            self.createPassword(password)
        
    def requestPassword(self):
        
        dialog = CustomDialog(title='Locked Folder', message='Enter your password', is_password=True)
        text = dialog.getText()
        if text:
            return text

    def requestNewPassword(self):
        
        dialog = CustomDialog(title='Locked Folder setup', message='choose a password', is_password=True)
        text=dialog.getText()
        if text:
            password=text
            dialog = CustomDialog(title='Locked Folder setup', message='confirm password', is_password=True)
            text=dialog.getText()
            if text:
                confirmed_password=text
                if password==confirmed_password:
                    if self.isValidPassword(password):
                        return password
                    else:
                        self.showErrorMessage("this is not a valid password")
                else:
                    self.showErrorMessage("Passwords do not match. Please make sure both fields are identical")
            else:
                return 0
        else:
            return 0
    def createPassword(self,password):
        if password:
                self.secure_folder.generate_master_key(password)

        
    def openLockedFolder(self):
        
        self.decrypted_files=[]
        im=ImagesModel()
        secure_files=im.get_secure_files()
        if not secure_files:
            self.showErrorMessage("Locked folder is empty!")
            return 0
        self.secure_folder=SecureFolder()
        if self.secure_folder.hasExistingPassword():
            self.password=self.requestPassword()
            if self.password is None:
                return 0
            if self.secure_folder.validate_password(self.password):
                for decrypted_file in secure_files:
                    decrypted_file_path=self.secure_folder.decrypt(decrypted_file,self.password)
                    if decrypted_file_path is not None:
                        self.decrypted_files.append(str(decrypted_file_path))
                if len(self.decrypted_files)<1:
                    #this is the rare case that the password is correct but decryption still failed
                    #this happens when there are decrypted files by another password or salt
                    self.showErrorMessage("Locked folder is empty!")
                    return 0

                self.close()
                self.main_widget.openLockedFolderGallery(self.decrypted_files,self.password)
            
            else:
                self.showErrorMessage("Password is incorrect!")
            
        else:
            password=self.requestNewPassword()
            self.createPassword(password)
        
    

    def isValidPassword(self,password):
        if password is None:
            return False
        elif len(password)<4:
            return False
        else:
            return True
    
    def removeFromLockedFolder(self):
        self.image_files.pop(self.current_index)
        self.main_widget.imageViewerDeleted(self.current_index)
        try:
            self.show_image()
        except:
            time.sleep(.1)
            self.current_index = self.current_index % len(self.image_files)
            self.show_image()
    def  BGR2GRAY(self):
        if self.edited_image is not None:
            img=self.edited_image
        else :
            image_path = self.image_files[self.current_index]
            img = cv2.imread(image_path)
        
        gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        gray_3C=cv2.merge([gray,gray,gray])

        self.edited_image=gray_3C
        self.edit_history.add(self.edited_image)
        
        self.show_edited_image()
        
       
        
    def rotateCCW(self):
        if self.edited_image is not None:
            img=self.edited_image
        else :
            image_path = self.image_files[self.current_index]
            img = cv2.imread(image_path)
        
        rotated_img = cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        self.edited_image = rotated_img
        self.edit_history.add(self.edited_image)  
        
        self.show_edited_image()

    def rotateCW(self):
        if self.edited_image is not None:
            img=self.edited_image
        else :
            image_path = self.image_files[self.current_index]
            img = cv2.imread(image_path)
        
        rotatedImg=cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)
        self.edited_image=rotatedImg
        self.edit_history.add(self.edited_image)
        
        self.show_edited_image()
    
    def flipH(self):
        if self.edited_image is not None:
            img=self.edited_image
        else :
            image_path = self.image_files[self.current_index]
            img = cv2.imread(image_path)
        
        
       
        flipped_img=cv2.flip(img, 1)
         
        self.edited_image = flipped_img
        self.edit_history.add(self.edited_image) 
        
        self.show_edited_image()
    def flipV(self):
        if self.edited_image is not None:
            img=self.edited_image
        else :
            image_path = self.image_files[self.current_index]
            img = cv2.imread(image_path)
        
        flipped_img=cv2.flip(img, 0)
        self.edited_image=flipped_img
        self.edit_history.add(self.edited_image)
        
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
        
        hsv_image = cv2.cvtColor(self.colors_transformation_image, cv2.COLOR_BGR2HSV)
        # Create a mask for pixels with high saturation
        saturation_mask = hsv_image[:, :, 1] > 10
        # Shift the hue channel by the specified value
        hsv_image[:, :, 1] = np.where(saturation_mask, np.clip(hsv_image[:, :, 1].astype(int) + offset_value, 0, 255), hsv_image[:, :, 1]).astype(np.uint8)

        

        self.colors_transformation_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

    def changeHue(self,shift_value):        
        hsv_image = cv2.cvtColor(self.colors_transformation_image, cv2.COLOR_BGR2HSV)
    
        # Shift the hue channel by the specified value
        hsv_image[:, :, 0] = ((hsv_image[:, :, 0].astype(float) + shift_value)% 180).astype(np.uint8) 
    
        # Convert the image back to BGR
        self.colors_transformation_image = cv2.cvtColor(hsv_image, cv2.COLOR_HSV2BGR)

    

    def change_brightness(self, brightness_offset):
        # Ensure brightness_offset is within the -100 to 100 range
        brightness_offset = max(-100, min(100, brightness_offset))
        
        # Convert brightness_offset to a factor
        # Map -100 to 0.5, 0 to 1.0, and 100 to 1.5
        brightness_factor = 1 + (brightness_offset / 200)

        # Convert the image to LAB color space
        lab = cv2.cvtColor(self.colors_transformation_image, cv2.COLOR_BGR2LAB)

        # Split the LAB image into L, A, and B channels
        l, a, b = cv2.split(lab)

        # Apply the brightness adjustment to the L channel
        l = np.clip(l.astype(float) * brightness_factor, 0, 255).astype(np.uint8)

        # Merge the color channels
        adjusted_lab = cv2.merge((l, a, b))

        # Convert the LAB image back to BGR color space
        self.colors_transformation_image = cv2.cvtColor(adjusted_lab, cv2.COLOR_LAB2BGR)


        
        
        
    def applyColorsTransformations(self,contrast_factor,brightness_offset,s_shift_value,shift_value):
        if self.edit_history.count>=1:
            self.colors_transformation_image= self.edit_history.peek()
        else:
            image_path = self.image_files[self.current_index]
            self.colors_transformation_image = cv2.imread(image_path)
        if contrast_factor!=100:        
            self.change_contrast(contrast_factor)
        if brightness_offset!=0:
            self.change_brightness(brightness_offset)
        if s_shift_value !=0:
            self.changeSaturation(s_shift_value)
        if shift_value!=0:
            self.changeHue(shift_value)
        
        self.edited_image=self.colors_transformation_image
        if (contrast_factor,brightness_offset,s_shift_value,shift_value)==(100,0,0,0):
            self.edited_image=self.edit_history.peek()
        #todo
        #self.edit_history.add(self.edited_image)
        self.show_edited_image()
        
    def finalizeAdjust(self):
        if self.edited_image is not None:
            self.edit_history.add(self.edited_image)

    
    def blurBackground(self):
        import rembg

        if self.edited_image is not None:
            img=self.edited_image
        else :
            image_path = self.image_files[self.current_index]
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
        self.edit_history.add(self.edited_image)
        self.show_edited_image()
    
    def scanQRC(self):
        
        decoded_list = decodeqr(Image.open(self.image_files[self.current_index]))
        
        for box in decoded_list:
            rpos_x, rpos_y = box.polygon[1]
            
            decoded_text = box.data.decode()
            if decoded_text:
                
                self.add_hyperlink_to_scene(f'{decoded_text[:20]}...',decoded_text,rpos_x,rpos_y)


    def add_hyperlink_to_scene(self, text, url, pos_x, pos_y):
        text_item = ClickableTextItem(text, url, self.scene)
        font = QFont("Arial", int(self.image_width*.015))
        text_item.setFont(font)
        text_item.setDefaultTextColor(QColor("blue"))
        text_item.setPos(pos_x, pos_y)
        
        # Calculate the bounding rectangle of the text
        text_rect = text_item.boundingRect()
        # Create a background rectangle with transparency
        rect_item = QGraphicsRectItem(QRectF(text_rect))
        # Set a transparent white background (alpha = 150, range 0-255)
        transparent_white = QColor(255, 255, 255, 150)  # Alpha 150 for transparency
        rect_item.setBrush(QBrush(transparent_white))
        # Remove the border by setting the pen to no pen
        rect_item.setPen(QPen(Qt.NoPen))
        # Position the background rectangle at the same position as the text
        rect_item.setPos(pos_x, pos_y)
        
        self.scene.addItem(rect_item)
        self.scene.addItem(text_item)
        
        # Store the rect_item in the text_item for later removal
        text_item.background_rect = rect_item

    

        
    def convert_cv_image_to_qpixmap(self, cv_image):
        # Check if the image has an alpha channel (4 channels)
        if cv_image.shape[2] == 4:
            # Convert from BGRA (OpenCV's default with alpha) to RGBA
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGRA2RGBA)
            height, width, channel = cv_image.shape
            bytes_per_line = 4 * width
            q_image = QImage(cv_image.data, width, height, bytes_per_line, QImage.Format_RGBA8888)
        else:
            # Convert from BGR to RGB (no alpha channel)
            cv_image = cv2.cvtColor(cv_image, cv2.COLOR_BGR2RGB)
            height, width, channel = cv_image.shape
            bytes_per_line = 3 * width
            q_image = QImage(cv_image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        
        return QPixmap.fromImage(q_image)



        
        
    def undo(self):
        #in case crop is initalized but not finalized
        self.cleanCrop()

        if self.edit_history.count>1:
            self.edit_history.pop()
            self.edited_image=self.edit_history.peek()
            self.show_edited_image()
        else:
                self.purge()
                self.show_image() 
    def checkZeroDisplacement(self):
        """
        an image can go through a series of transformations that makes it efficefively equivalent to the orignal image
        eg: rotation 4 times (or multiple) in the same direction or flipping twice (or multiple)
        Args:
            None

        Returns:
            Boolen
            
        """
        if self.edited_image is not None:
            img_path = self.image_files[self.current_index]
            original_img=cv2.imread(img_path)
            if original_img.shape ==self.edited_image.shape:
                if np.array_equal(original_img,self.edited_image):
                    return True
                else:
                    return False
                
            else:
                return False
        else:
            return True
                
        
        
    def revert(self):
        self.purge()
        self.show_image()
    def purge(self):
        """
        Clears and releases the following resources: edited_image, edit_history , scene. 
        as well as Runs the garbage collector and closes no longer needed widgets 
        """
        self.edited_image=None
        self.edit_history.clear()
        #in case crop is initalized but not finalized
        self.cleanCrop()
        
        
        self.scene.clear()
        gc.collect()
    def cleanCrop(self):
        if hasattr(self, 'crop_rect'):
            self.rightBrowse.setVisible(True)
            self.leftBrowse.setVisible(True)
            delattr(self,'crop_rect')

    def save_image(self):
        if not self.checkZeroDisplacement():
            img_path=self.image_files[self.current_index]
            msg_box = SavingMessageBox(img_path,self.edited_image)
            msg_box.exec_()
            choice = msg_box.get_choice()
            
            if choice=="overwrite":
                cv2.imwrite(img_path, self.edited_image)
                file_name=img_path
            if choice=="copy":
                mod_time = datetime.datetime.now().strftime("%Y-%m-%d-%H%M%S")
                path = os.path.splitext(img_path)
                file_name=f"{path[0]}_{mod_time}{path[-1]}"
                cv2.imwrite(file_name,self.edited_image)
                
            saved={'index':self.current_index,'choice':choice,'file_name':file_name}
            self.main_widget.imageViewerSaved(saved)
            
            self.edited_image=None
            self.edit_history.clear()
            
            
            
            
            
        else:
            self.showErrorMessage("no changes were made!")
    
    def delete_image(self):
        self.purge()
        file_name=self.image_files[self.current_index]
        if os.path.exists(file_name):
            
            try:
                os.system(f"gio trash '{self.image_files[self.current_index]}'")

            except OSError as e:
                print(f"Error moving file to trash: {e.filename} - {e.strerror}")
            
            self.image_files.pop(self.current_index)
            self.main_widget.imageViewerDeleted(self.current_index)
            try:
                self.show_image()
            except:
                time.sleep(.1)
                self.current_index = self.current_index % len(self.image_files)
                self.show_image()
            
           
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
        pixmap = QPixmap(get_media_path('warning.png')).scaledToWidth(150)
        msg_box.setIconPixmap(pixmap)
        msg_box.setText(msg)
        msg_box.setWindowTitle('Warning')
        msg_box.exec_()
    
    


    def show_containing_folder(self):
        image_path = self.image_files[self.current_index]
        dir_path = image_path[0:image_path.rfind('/')]
        
        commands = [
            (["nautilus", "--select", image_path], "GNOME"),  # For GNOME desktop environment
            (["nemo", image_path], "Cinnamon"),               # For Cinnamon desktop environment
            (["xdg-open", dir_path], "Generic XDG"),          # For most desktop environments
            (["thunar", dir_path], "XFCE")                    # For XFCE desktop environment
        ]
        
        for command, env in commands:
            try:
                subprocess.run(command, check=True, timeout=3)  # timeout for responsiveness
                print(f"Opened folder using {env}")
                return True
            except subprocess.CalledProcessError:
                continue
            except subprocess.TimeoutExpired:
                print(f"Command for {env} timed out")
                continue
            except Exception as e:
                print(f"An error occurred: {e}")
                continue
        
        return False



    
    def closeEvent(self, event):
        
        self.purge()
        self.finishedSignal.emit()
        event.accept()
        



class InfoWidget(QWidget):
    def __init__(self):
        '''
        this info widget is only for app description and information not error messages and what not
        '''
        super().__init__()
        with open(get_config_path('config.yaml'), 'r') as file:
            self.config_data = yaml.safe_load(file)
        self.setStyleSheet(f"background-color: {self.config_data['background']};color:white;"
                          )
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Info')
        self.setGeometry(500, 200, 400, 300)

        layout = QVBoxLayout()

        horizontal_layout = QHBoxLayout()

        # Image Label
        image_label = QLabel(self)
        pixmap = QPixmap(get_media_path('info.png')).scaledToWidth(150)
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
        website_button.clicked.connect(lambda: QDesktopServices.openUrl(QUrl('https://ogalleryapp.github.io/')))
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
class OGSlider(QSlider):
    def __init__(self, orientation,default_value, parent=None):
        super().__init__(orientation, parent)
        self.default_value=default_value
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.setValue(self.default_value)
        #super().mouseDoubleClickEvent(event) //this is intentional


class Adjust(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
    
        self.contrast_offset = self.contrast_default= 100
        self.saturation_offset = self.saturation_default=0
        self.hue_offset = self.hue_deafult=0
        self.brightness_offset = self.brightness_default= 0
        
        self.init_ui()

    def init_ui(self):
        self.setWindowFlags(Qt.Window)
        self.setWindowTitle('adjust')
        self.setGeometry(300, 100, 400, 400)
        self.setStyleSheet(f"background-color: #212121;color:'white';")
        self.contrast_label = QLabel('Contrast:', self)
        self.contrast_slider = OGSlider(Qt.Horizontal,self.contrast_default)
        self.contrast_slider.setMinimum(30)
        self.contrast_slider.setMaximum(200)
        self.contrast_slider.setValue(100)
        self.contrast_slider.valueChanged.connect(self.update_contrast_offset)
        self.contrast_value_label = QLabel(str(self.contrast_slider.value()), self)
        self.contrast_value_label.setText("1")
        
        self.brightness_label = QLabel('Brightness:', self)
        self.brightness_slider = OGSlider(Qt.Horizontal,self.brightness_default)
        self.brightness_slider.setMinimum(-100)
        self.brightness_slider.setMaximum(100)
        self.brightness_slider.setValue(0)
        self.brightness_slider.valueChanged.connect(self.update_brightness_offset)
        self.brightness_value_label = QLabel(str(self.brightness_slider.value()), self)

        self.hue_label = QLabel('Hue:', self)
        self.hue_slider = OGSlider(Qt.Horizontal,self.hue_deafult)
        self.hue_slider.setMinimum(0)
        self.hue_slider.setMaximum(180)
        self.hue_slider.setValue(0)
        self.hue_slider.valueChanged.connect(self.update_hue_offset)
        self.hue_value_label = QLabel(str(self.hue_slider.value()), self)

        self.saturation_label = QLabel('saturation:', self)
        self.saturation_slider = OGSlider(Qt.Horizontal,self.saturation_default)
        self.saturation_slider.setMinimum(-100)
        self.saturation_slider.setMaximum(100)
        self.saturation_slider.setValue(0)
        self.saturation_slider.valueChanged.connect(self.update_saturation_offset)
        self.saturation_value_label = QLabel(str(self.saturation_slider.value()), self)


        self.timer = QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.applyAdjustments)
        
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

        #slow is smooth and smooth is fast. when applying every little change instantly it takes a lot of unneccessary resources
        #which slows down the widget
        self.contrast_slider.valueChanged.connect(lambda:self.timer.start(50))
        self.brightness_slider.valueChanged.connect(lambda:self.timer.start(50))
        self.saturation_slider.valueChanged.connect(lambda:self.timer.start(50))
        self.hue_slider.valueChanged.connect(lambda:self.timer.start(50))

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
        
    
    def keyPressEvent(self, event):
            if (event.key() == Qt.Key_Backspace) or (event.key() == Qt.Key_Escape):
                self.close()

    def closeEvent(self, event):
        self.parent().finalizeAdjust()
        event.accept()
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
        with open(get_config_path('config.yaml'), 'r') as file:
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
            "#c1c100",
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
        dynamic_config_path=f"/home/{os.getenv('USER')}/.config/OpenGallery/config.yaml"
        
        with open(dynamic_config_path, 'r') as file:
            self.dynamic_config_data = yaml.safe_load(file)      
            
        self.dynamic_config_data['style_color'] = color
        
        with open(dynamic_config_path, 'w') as file:
            yaml.dump(self.dynamic_config_data, file)
        self.colorChanged.emit(color)
    
    def clearBorders(self):
        for button in self.colors_buttons:
            button.setStyleSheet(button.styleSheet().replace("border: 2px solid white;", ""))
    
    def getImagesPaths(self):
        username = os.getenv('USER')
        images_directories = []  # Initialize with an empty list

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
    def __init__(self, graphics_view):
        super().__init__()
        self.opened_menu = None
        with open(get_config_path('config.yaml'), 'r') as file:
            self.config_data = yaml.safe_load(file)
        self.graphics_view = graphics_view

    def eventFilter(self, obj, event):
        if obj is self.graphics_view and event.type() == QEvent.ContextMenu:
            if self.opened_menu is not None:
                self.opened_menu.close()
            menu = QMenu()

            copy_action = QAction("Copy", menu)
            copy_action.triggered.connect(lambda: self.copy_signal.emit())
            menu.addAction(copy_action)

            delete_action = QAction("Delete", menu)
            delete_action.triggered.connect(lambda:self.delete_signal.emit())
            menu.addAction(delete_action)


            show_folder_action = QAction("Show Containing Folder", menu)
            show_folder_action.triggered.connect(lambda:self.show_folder.emit())
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

class PanningGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragMode(QGraphicsView.NoDrag)
        self.setRenderHint(QPainter.Antialiasing)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setFrameShape(QFrame.NoFrame)
        self.panning = False
        self.pan_start_x = 0
        self.pan_start_y = 0

    def is_crop_rect(self, item):
        return isinstance(item, CornerBasedRectItem)

    def mousePressEvent(self, event):
        item = self.itemAt(event.pos())
        if event.button() == Qt.LeftButton and not self.is_crop_rect(item):
            self.panning = True
            self.pan_start_x = event.x()
            self.pan_start_y = event.y()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.panning:
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - (event.x() - self.pan_start_x))
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - (event.y() - self.pan_start_y))
            self.pan_start_x = event.x()
            self.pan_start_y = event.y()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton and self.panning:
            self.panning = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        factor = 1.1 if event.angleDelta().y() > 0 else 0.9
        self.scale(factor, factor)



class ClickableTextItem(QGraphicsTextItem):
    def __init__(self, html_text, url, scene, parent=None):
        super().__init__(html_text, parent)
        self.url = url
        self.scene = scene
        self.background_rect = None

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            QDesktopServices.openUrl(QUrl(self.url))
            if self.background_rect:
                self.scene.removeItem(self.background_rect)
            self.scene.removeItem(self)



class CircularBuffer:
    def __init__(self, size):
        self.size = size
        self.buffer = [None] * size
        self.head = 0
        self.tail = 0
        self.full = False
        self.count = 0  

    def add(self, item):
        if self.count < self.size:
            self.buffer[self.head] = item
            self.head = (self.head + 1) % self.size
            self.count += 1
        else:
            self.buffer[self.head] = item
            self.head = (self.head + 1) % self.size
            self.tail = (self.tail + 1) % self.size
        self.full = self.head == self.tail

    def pop(self):
        if self.count == 0:
            return None
        self.head = (self.head - 1 + self.size) % self.size
        item = self.buffer[self.head]
        self.buffer[self.head] = None
        self.count -= 1
        self.full = False
        return item
    def peek(self):
        '''
        Returns the most recent item
        Argrs:
            None
        Returns:
            most recent item (numpy array)
        '''
        if self.count == 0:
            return None
        
        last_index = (self.head - 1 + self.size) % self.size
        return self.buffer[last_index]
    def clear(self):
        self.buffer = [None] * self.size
        self.head = 0
        self.tail = 0
        self.full = False
        self.count = 0 

    def get_buffer(self):
        if self.full:
            return self.buffer[self.tail:] + self.buffer[:self.tail]
        elif self.head > self.tail:
            return self.buffer[self.tail:self.head]
        else:
            return self.buffer[self.tail:] + self.buffer[:self.head]


from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import Qt, QRectF, QPointF
from PyQt5.QtGui import QPen, QPainter, QPainterPath

class CornerBasedRectItem(QGraphicsItem):
    def __init__(self, x, y, width, height, image_width, image_height, parent=None):
        super().__init__(parent)
        self.x0 = x
        self.y0 = y
        self.x1 = x + width
        self.y1 = y
        self.x2 = x
        self.y2 = y + height
        self.x3 = x + width
        self.y3 = y + height
        self.image_width = image_width
        self.image_height = image_height
        self.dragging = None
        self.drag_start = None
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.setAcceptHoverEvents(True)

    def boundingRect(self):
        return QRectF(min(self.x0, self.x1, self.x2, self.x3),
                      min(self.y0, self.y1, self.y2, self.y3),
                      max(self.x0, self.x1, self.x2, self.x3) - min(self.x0, self.x1, self.x2, self.x3),
                      max(self.y0, self.y1, self.y2, self.y3) - min(self.y0, self.y1, self.y2, self.y3))

    def paint(self, painter, option, widget=None):
        painter.setPen(QPen(Qt.red, 2))
        painter.drawRect(self.boundingRect())
        if self.isSelected():
            painter.setPen(QPen(Qt.blue, 2, Qt.DashLine))
            painter.drawRect(self.boundingRect())

    def mousePressEvent(self, event):
        self.dragging = self.get_drag_area(event.pos())
        self.drag_start = event.pos()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.dragging:
            delta = event.pos() - self.drag_start
            if self.dragging == 'left':
                new_x = self.x0 + delta.x()
                if 0 <= new_x < self.x1 - 100:
                    self.x0 = self.x2 = new_x
            elif self.dragging == 'right':
                new_x = self.x1 + delta.x()
                if self.x0 + 100 < new_x <= self.image_width:
                    self.x1 = self.x3 = new_x
            elif self.dragging == 'top':
                new_y = self.y0 + delta.y()
                if 0 <= new_y < self.y2 - 100:
                    self.y0 = self.y1 = new_y
            elif self.dragging == 'bottom':
                new_y = self.y2 + delta.y()
                if self.y0 + 100 < new_y <= self.image_height:
                    self.y2 = self.y3 = new_y
            elif self.dragging == 'move':
                new_x0 = self.x0 + delta.x()
                new_y0 = self.y0 + delta.y()
                if 0 <= new_x0 and new_x0 + (self.x1 - self.x0) <= self.image_width and \
                   0 <= new_y0 and new_y0 + (self.y2 - self.y0) <= self.image_height:
                    self.x0 += delta.x()
                    self.y0 += delta.y()
                    self.x1 += delta.x()
                    self.y1 += delta.y()
                    self.x2 += delta.x()
                    self.y2 += delta.y()
                    self.x3 += delta.x()
                    self.y3 += delta.y()
            self.drag_start = event.pos()
            self.update()
            self.scene().update()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        self.dragging = None
        super().mouseReleaseEvent(event)

    def hoverMoveEvent(self, event):
        drag_area = self.get_drag_area(event.pos())
        if drag_area:
            self.setCursor(self.get_cursor_for_area(drag_area))
        else:
            self.setCursor(Qt.OpenHandCursor)
        super().hoverMoveEvent(event)

    def hoverLeaveEvent(self, event):
        self.unsetCursor()
        super().hoverLeaveEvent(event)

    def get_drag_area(self, pos):
        margin = 10  # pixels
        if abs(pos.x() - self.x0) < margin and self.y0 < pos.y() < self.y2:
            return 'left'
        elif abs(pos.x() - self.x1) < margin and self.y1 < pos.y() < self.y3:
            return 'right'
        elif abs(pos.y() - self.y0) < margin and self.x0 < pos.x() < self.x1:
            return 'top'
        elif abs(pos.y() - self.y2) < margin and self.x2 < pos.x() < self.x3:
            return 'bottom'
        elif self.x0 < pos.x() < self.x1 and self.y0 < pos.y() < self.y2:
            return 'move'
        return None

    def get_cursor_for_area(self, area):
        if area in ['left', 'right']:
            return Qt.SizeHorCursor
        elif area in ['top', 'bottom']:
            return Qt.SizeVerCursor
        elif area == 'move':
            return Qt.ClosedHandCursor
        return Qt.ArrowCursor

    def get_relative_coordinates(self):
        return {
            'x': int(min(self.x0, self.x1, self.x2, self.x3)),
            'y': int(min(self.y0, self.y1, self.y2, self.y3)),
            'width': int(max(self.x0, self.x1, self.x2, self.x3) - min(self.x0, self.x1, self.x2, self.x3)),
            'height': int(max(self.y0, self.y1, self.y2, self.y3) - min(self.y0, self.y1, self.y2, self.y3))
        }       
def run_gui():
    app = QApplication([])   
    app.setApplicationName("Ogallery") 
    app.setStyleSheet("QToolTip { color: #ffffff; background-color: #000000; border: 1px solid white; }")  
    main_widget = MainWidget()
    app.exec_()


def run_inference_model():
    from models.MobileNet import Model
    model=Model()
    model.predictAndSave()
    

                
if __name__ == '__main__':
    gui_process = multiprocessing.Process(target=run_gui)
    inference_process = multiprocessing.Process(target=run_inference_model)
 
    
    gui_process.start()
    inference_process.start()

    gui_process.join()
    inference_process.join()
