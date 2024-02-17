#from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont

class OStyle:
    def __init__(self):
        self.color = Color()
        self.size = Size()
class Color:
    def __init__(self):
        self.background="#212121"
        self.hover_default="#2e2e2e"
        self.gray="#212121"
        self.light_gray="#2e2e2e"
        self.blue = "#00347d"
        self.royal_blue="#0f68db"
        self.red = "#7d0000"

class Size:
    def __init__(self):
        self.standard_icon_size="25px"

        self.large_font = QFont()
        self.large_font.setPointSize(20)

