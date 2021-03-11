from PyQt5.QtWidgets import QLabel
from re import search as RE_search

class QLabel_File_Dragable(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        path_list = e.mimeData().text().replace('file:///', '').split('\n')

        if len(path_list) > 1:
            path_list.pop()

        if RE_search('(jpg|jpeg|png|webp|bmp|tif|tga|JPG|JPEG|PNG|WEBP|BMP|TIF|TGA)$',path_list[0]):
            self.functional_arithmetic.Import_image(path_list)
        else:
            self.functional_arithmetic.Import_path(path_list[0])