import os
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton,QSizePolicy
from PyQt5.QtGui import QColor  
from PyQt5.QtGui import QImage
import cv2
import numpy as np
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = '/path/to/your/qt/plugins'

class PathInputWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Directory Input')
        self.setGeometry(100, 100, 400, 100)

        layout = QVBoxLayout(self)

        self.path_edit = QLineEdit(self)
        layout.addWidget(self.path_edit)

        open_button = QPushButton('Open Image Viewer', self)
        open_button.clicked.connect(self.open_image_viewer)
        layout.addWidget(open_button)

        self.show()

    def open_image_viewer(self):
        directory_path = self.path_edit.text()
        if os.path.isdir(directory_path):
            self.viewer = ImageViewer(directory_path)
            self.viewer.show()  # Show the ImageViewer
            self.close()
        else:
            # Handle invalid directory path
            pass

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or Qt.Key_Return:
            self.open_image_viewer()
            
class ImageViewer(QWidget):
    def __init__(self, directory_path):
        super().__init__()

        self.directory_path = directory_path
        self.file_list = []
        self.current_index = 0
        self.primary_screen = QDesktopWidget().screenGeometry()
        self.screen_width = self.primary_screen.width()
        self.screen_height = self.primary_screen.height()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Image Viewer')
        self.setGeometry(100, 100, 800, 600)

        self.setStyleSheet("background-color: #222324;")
        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.file_list = []
        self.current_index = 0

        self.load_images()
        #---------------------layouts-----------------------------------
        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)
        button_layout = QHBoxLayout()  
        layout.addLayout(button_layout)
        
        #-----------process/invert button(to be deleted)-----------
        self.process_button = QPushButton('Invert', self)
        self.process_button.setFocusPolicy(Qt.NoFocus)
        self.process_button.clicked.connect(self.process_image)
        button_layout.addWidget(self.process_button)    

        #---------------Gray button---------------------------
        self.gray_button = QPushButton('Gray scale', self)
        self.gray_button.setFocusPolicy(Qt.NoFocus)
        self.gray_button.clicked.connect(self.BGR2GRAY)
        button_layout.addWidget(self.gray_button)
        
        #-------------- gaussian blur button-----------------
        self.gaussianBlur_button = QPushButton('smooth', self)
        self.gaussianBlur_button.setFocusPolicy(Qt.NoFocus)
        self.gaussianBlur_button.clicked.connect(self.gaussianBlur)
        button_layout.addWidget(self.gaussianBlur_button)
        
        
        #----------------Rotate button------------------------------------
        self.rotate_button = QPushButton('↶', self)
        self.rotate_button.setFocusPolicy(Qt.NoFocus)
        self.rotate_button.clicked.connect(self.rotateCCW)
        button_layout.addWidget(self.rotate_button)
        
        
        
        #--------------Exposure slider/button--------------------------------

        
        self.exposure_slider = QSlider(Qt.Horizontal)
        self.exposure_slider.setMinimum(0)
        self.exposure_slider.setMaximum(200)
        self.exposure_slider.setValue(100)  # Set an initial value
        self.exposure_slider.valueChanged.connect(self.update_exposure)
        self.exposure_slider.hide()
        layout.addWidget(self.exposure_slider)
        
        self.set_exposure_button = QPushButton('Exposure', self)
        self.set_exposure_button.setFocusPolicy(Qt.NoFocus)

        self.set_exposure_button.clicked.connect(self.toggle_exposure_slider)
        button_layout.addWidget(self.set_exposure_button)
        
        
        self.save_button = QPushButton('💾', self)
        self.save_button.setFocusPolicy(Qt.NoFocus)
        self.save_button.clicked.connect(self.save_image)
        button_layout.addWidget(self.save_button)
        
      # Set background color for all buttons
        button_style = "QPushButton { background-color: #212121; color: white; }"
        
        self.process_button.setStyleSheet(button_style)
        self.gray_button.setStyleSheet(button_style)
        self.gaussianBlur_button.setStyleSheet(button_style)
        self.rotate_button.setStyleSheet(button_style)
        self.save_button.setStyleSheet(button_style)
        self.set_exposure_button.setStyleSheet(button_style)
        
        #-----------------------------------------------------
        self.image_label.setFocusPolicy(Qt.StrongFocus)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


        self.load_images()

        self.show_image()

        self.show()

    def load_images(self):
        if self.directory_path:
            self.file_list = [os.path.join(self.directory_path, file) for file in os.listdir(self.directory_path)
                              if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

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
        if event.key() == Qt.Key_Right:
            self.next_image()
        elif event.key() == Qt.Key_Left:
            self.previous_image()

    def next_image(self):
        self.current_index = (self.current_index + 1) % len(self.file_list)
        self.show_image()

    def previous_image(self):
        self.current_index = (self.current_index - 1) % len(self.file_list)
        self.show_image()
    def process_image(self):
            if hasattr(self, 'edited_image'):
                img=self.edited_image
            else :
                image_path = self.file_list[self.current_index]
                img = cv2.imread(image_path)

            inverted_img = 255 - img
            self.edited_image=inverted_img
            pixmap = self.convert_cv_image_to_qpixmap(inverted_img)
            self.image_label.setPixmap(pixmap.scaled(round(self.screen_width*.8),round(self.screen_height*.8),Qt.KeepAspectRatio, Qt.SmoothTransformation))
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
        self.image_label.setPixmap(pixmap.scaled(round(self.screen_width*.8),round(self.screen_height*.8),Qt.KeepAspectRatio, Qt.SmoothTransformation))
    
    def gaussianBlur(self):
        if hasattr(self, 'edited_image'):
            img=self.edited_image
        else :
            image_path = self.file_list[self.current_index]
            img = cv2.imread(image_path)
        Blurred_img=cv2.GaussianBlur(img,ksize=(3,3),sigmaX=1)
        self.edited_image=Blurred_img
        pixmap = self.convert_cv_image_to_qpixmap(Blurred_img)
        self.image_label.setPixmap(pixmap.scaled(round(self.screen_width*.8),round(self.screen_height*.8),Qt.KeepAspectRatio, Qt.SmoothTransformation))
    
    def rotateCCW(self):
        if hasattr(self, 'edited_image'):
            img=self.edited_image
        else :
            image_path = self.file_list[self.current_index]
            img = cv2.imread(image_path)
        rotatedImg=cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        self.edited_image=rotatedImg
        pixmap = self.convert_cv_image_to_qpixmap(rotatedImg)
        self.image_label.setPixmap(pixmap.scaled(round(self.screen_width*.8),round(self.screen_height*.8),Qt.KeepAspectRatio, Qt.SmoothTransformation))
    

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
        self.image_label.setPixmap(pixmap.scaled(round(self.screen_width*.8),round(self.screen_height*.8),Qt.KeepAspectRatio, Qt.SmoothTransformation))
    
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
    def show_success_message(self):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setText("Saved successfully!")
        msg_box.setWindowTitle("Success")
        msg_box.exec_()
        
if __name__ == '__main__':
    app = QApplication([])

    
    
    
    path_input_widget = PathInputWidget()

    app.exec_()
