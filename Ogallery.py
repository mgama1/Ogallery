import os
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QFileDialog,QHBoxLayout,QMessageBox
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton,QSizePolicy
from PyQt5.QtGui import QColor  # Add this import statement
from PyQt5.QtGui import QImage
import cv2
import os
os.environ['QT_QPA_PLATFORM_PLUGIN_PATH'] = '/path/to/your/qt/plugins'

class ImageViewer(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        self.setWindowTitle('Image Viewer')
        self.setGeometry(100, 100, 800, 600)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)

        self.file_list = []
        self.current_index = 0

        self.load_images()

        layout = QVBoxLayout(self)
        layout.addWidget(self.image_label)
        
        button_layout = QHBoxLayout()  # Add a QHBoxLayout for the buttons
        layout.addLayout(button_layout)
        self.process_button = QPushButton('Process Image', self)
        self.process_button.setFocusPolicy(Qt.NoFocus)
        self.process_button.clicked.connect(self.process_image)
        button_layout.addWidget(self.process_button)    

        self.gray_button = QPushButton('gray Image', self)
        self.gray_button.setFocusPolicy(Qt.NoFocus)
        self.gray_button.clicked.connect(self.BGR2GRAY)
        button_layout.addWidget(self.gray_button)
        
        self.gaussianBlur_button = QPushButton('Blur', self)
        self.gaussianBlur_button.setFocusPolicy(Qt.NoFocus)
        self.gaussianBlur_button.clicked.connect(self.gaussianBlur)
        button_layout.addWidget(self.gaussianBlur_button)
        
        
        
        self.rotate_button = QPushButton('↶', self)
        self.rotate_button.setFocusPolicy(Qt.NoFocus)
        self.rotate_button.clicked.connect(self.rotateCCW)
        button_layout.addWidget(self.rotate_button)
        
        
        
        self.save_button = QPushButton('💾', self)
        self.save_button.setFocusPolicy(Qt.NoFocus)
        self.save_button.clicked.connect(self.save_image)
        button_layout.addWidget(self.save_button)

        
        
        self.image_label.setFocusPolicy(Qt.StrongFocus)
        self.image_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.show_image()

        self.show()

    def load_images(self):
        directory = QFileDialog.getExistingDirectory(self, 'Select Directory')
        if directory:
            self.file_list = [os.path.join(directory, file) for file in os.listdir(directory)
                              if file.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))]

    def show_image(self):
        if self.file_list:
            image_path = self.file_list[self.current_index]
            pixmap = QPixmap(image_path)
            self.image_label.setPixmap(pixmap.scaledToWidth(self.width()/2, Qt.SmoothTransformation))
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
        if self.file_list:
            image_path = self.file_list[self.current_index]

            # Load the image using OpenCV
            img = cv2.imread(image_path)

            # Invert the colors using NumPy operations
            inverted_img = 255 - img
            self.edited_image=inverted_img
            # Display the processed image
            pixmap = self.convert_cv_image_to_qpixmap(inverted_img)
            self.image_label.setPixmap(pixmap.scaledToWidth(self.width() / 2, Qt.SmoothTransformation))
    def  BGR2GRAY(self):
        if self.file_list:
            image_path = self.file_list[self.current_index]
        img = cv2.imread(image_path)
        gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY) 
        gray_3C=cv2.merge([gray,gray,gray])
        
        self.edited_image=gray_3C
        pixmap = self.convert_cv_image_to_qpixmap(gray_3C)
        self.image_label.setPixmap(pixmap.scaledToWidth(self.width() / 2, Qt.SmoothTransformation))
    
    def gaussianBlur(self):
        if hasattr(self, 'edited_image'):
            img=self.edited_image
        else :
            image_path = self.file_list[self.current_index]
            img = cv2.imread(image_path)
        Blurred_img=cv2.GaussianBlur(img,ksize=(9,9),sigmaX=9)
        self.edited_image=Blurred_img
        pixmap = self.convert_cv_image_to_qpixmap(Blurred_img)
        self.image_label.setPixmap(pixmap.scaledToWidth(self.width() / 2, Qt.SmoothTransformation))
    
    def rotateCCW(self):
        if hasattr(self, 'edited_image'):
            img=self.edited_image
        else :
            image_path = self.file_list[self.current_index]
            img = cv2.imread(image_path)
        rotatedImg=cv2.rotate(img, cv2.ROTATE_90_COUNTERCLOCKWISE)
        self.edited_image=rotatedImg
        pixmap = self.convert_cv_image_to_qpixmap(rotatedImg)
        self.image_label.setPixmap(pixmap.scaledToWidth(self.width() / 2, Qt.SmoothTransformation))
    
     

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
    viewer = ImageViewer()
    app.exec_()
