from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtCore import Qt

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


