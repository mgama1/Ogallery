       
import qtawesome as qta
from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt,QTimer
import yaml
import time
import os
from .imageThumbnail import ImageThumbnailWidget

class ImageGalleryApp(QMainWindow):
    def __init__(self,main_widget):
        super().__init__()
        with open('config/config.yaml', 'r') as file:
            self.config_data = yaml.safe_load(file)

        self.main_widget = main_widget  # Keep a reference to MainWidget 
        self.image_files = self.main_widget.images
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

        # Create the main vertical layout
        main_layout = QVBoxLayout()

        # Create a scroll area for the grid layout
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_content = QWidget()
        scroll_area.setWidget(scroll_content)

        # Create the grid layout and add it to the scroll content
        self.grid_layout = QGridLayout()
        scroll_content.setLayout(self.grid_layout)

        # Add thumbnails to the grid layout
        row, col = 0, 0
        for index, image_file in enumerate(self.image_files):
            thumbnail_widget = ImageThumbnailWidget(image_file, self.image_files, self.config_data, self.main_widget)
            thumbnail_widget.selectedSig.connect(lambda selected_index: self.selected_indices.append(selected_index))
            self.grid_layout.addWidget(thumbnail_widget, row, col)
            self.thumbnail_widgets.append(thumbnail_widget) 
            
            col += 1
            if col == 3:
                col = 0
                row += 1

        # Add the scroll area to the main layout
        main_layout.addWidget(scroll_area)

        # Create a horizontal layout for the button to center it
        button_layout = QHBoxLayout()
        button_layout.setContentsMargins(0, 0, 0, 0)  # Set margins around the layout to zero
        #button_layout.addStretch()  # Add stretchable space before the button
        self.backToTopButton = QPushButton(self)
        self.backToTopButton.setVisible(0)
        self.visiblity_timer = QTimer()
        self.visiblity_timer.setSingleShot(True)  
        self.visiblity_timer.timeout.connect(lambda:self.backToTopButton.setVisible(False))
        #ph.caret-up-fill
        #
        self.backToTopButton.setIcon(qta.icon('msc.chevron-up', color='white',scale_factor=2))
        self.backToTopButton.setStyleSheet("margin: 0px; padding: 0px;border: none;")  # Remove margin and padding
        #self.button.setFixedSize(20, 20)  # Set the button size to 50x50
        button_layout.addWidget(self.backToTopButton)
        #button_layout.addStretch()  # Add stretchable space after the button

        # Create a widget to hold the button layout and add it to the main layout
        button_widget = QWidget()
        button_widget.setLayout(button_layout)
        main_layout.addWidget(button_widget)  # Add the button at the bottom of the layout

        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)
        
        # Connect the scrollbar value change event to load more thumbnails
        self.scroll = scroll_area.verticalScrollBar()
        self.scroll.valueChanged.connect(self.loadNextBatch)
        #go back to Top
        self.backToTopButton.clicked.connect(lambda:self.scroll.setValue(0))

        self.setGeometry(300, 100, 800, 650)
        self.setWindowTitle('OGallery')
        self.show()
        self.load_initial_batch()
        
    def load_initial_batch(self):
        for i in range(min(self.initial_batch,len(self.thumbnail_widgets))):
            self.thumbnail_widgets[self.loaded_count].load_thumbnail()
            self.loaded_count += 1

    def loadNextBatch(self):
        self.backToTopButton.setVisible(True)  # Show the button when scrolling
        self.visiblity_timer.start(2000)  # Start a timer for x seconds to hide the button
        
        self.scroll_value = self.scroll.value()
        if self.scroll_value >= self.scrollbar_threshold:
            for i in range(min(len(self.thumbnail_widgets), self.batch_size)):
                if self.loaded_count < len(self.image_files):  # Load only if there's more to load
                    self.thumbnail_widgets[self.loaded_count].load_thumbnail()
                    self.loaded_count += 1
            self.scrollbar_threshold += 20  # Adjust the threshold by a fixed amount

            
    def updateThumbnail(self, saved):
        self.edited_index=saved["index"]
        choice=saved["choice"]
        file_name=saved["file_name"]
        
        if self.edited_index >= len(self.thumbnail_widgets):
            return
        if choice=='overwrite':
            thumbnail_widget = self.thumbnail_widgets.pop(self.edited_index)
            self.grid_layout.removeWidget(thumbnail_widget)
            thumbnail_widget.deleteLater()  
            #reload the thumbnail widget from disk
            nthumbnail_widget = ImageThumbnailWidget(self.image_files[self.edited_index], self.image_files,self.config_data,self.main_widget)
            nthumbnail_widget.load_thumbnail()
            
            nthumbnail_widget.selectedSig.connect(lambda selected_index:self.selected_indices.append(selected_index))
        if choice=='copy':
            #reload the thumbnail widget from disk
            nthumbnail_widget = ImageThumbnailWidget(file_name, self.image_files,self.config_data,self.main_widget)
            nthumbnail_widget.load_thumbnail()
            self.image_files.insert(self.edited_index,file_name)
            
            nthumbnail_widget.selectedSig.connect(lambda selected_index:self.selected_indices.append(selected_index))
        else:
            pass
        
        self.thumbnail_widgets.insert(self.edited_index, nthumbnail_widget)
        self.loaded_count =   0  
        row, col = 0, 0
        for i, widget in enumerate(self.thumbnail_widgets):
            self.grid_layout.addWidget(widget, row, col)
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

    def refreshLayout(self):
        # Clear the layout
        for i in reversed(range(self.grid_layout.count())):
            self.grid_layout.itemAt(i).widget().setParent(None)
    
        # Re-add remaining thumbnails to the layout
        row, col = 0, 0
        for i, widget in enumerate(self.thumbnail_widgets):
            self.grid_layout.addWidget(widget, row, col)
            col += 1
            if col == 3:
                col = 0
                row += 1

    def removeThumbnail(self, thumbnail_index):
        thumbnail_widget = self.thumbnail_widgets.pop(thumbnail_index)
        self.grid_layout.removeWidget(thumbnail_widget)
        thumbnail_widget.deleteLater()  # Delete the widget to free up resources

        self.refreshLayout()
    

    def removeThumbnails(self, thumbnails_indices_list):
        # Sort indices in reverse order to avoid index shifting issues
        thumbnails_indices_list.sort(reverse=True)
        for thumbnail_index in thumbnails_indices_list:
            thumbnail_widget = self.thumbnail_widgets.pop(thumbnail_index)
            os.system(f"gio trash '{self.image_files[thumbnail_index]}'")
            self.image_files.pop(thumbnail_index)
            self.grid_layout.removeWidget(thumbnail_widget)
            thumbnail_widget.deleteLater()  # Delete the widget to free up resources
    
        self.refreshLayout()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Backspace or event.key() == Qt.Key_Escape:
            self.close()        

        if event.key() == Qt.Key_Delete:
            self.removeThumbnails(self.getIndicesToDelete())
            
        if event.key() == Qt.Key_T:
            self.scroll.setValue(0)