from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QLabel, QVBoxLayout
import numpy as np
from PIL import Image, ImageQt
from Classes.Series import Series
from MAIA import MAIA


class PatientMiniView(QLabel):
    set_focus = pyqtSignal(list)

    def __init__(self, parent, series_info, miniature, position):
        super().__init__()
        self.setParent(parent)
        self.position = position
        self.init_view(series_info, miniature)

    def init_view(self, info, mini):
        self.setFixedHeight(self.parent().maximumWidth())
        self.setStyleSheet('QLabel {background:rgb(200,200,200)}')

        date = str(info.get('ContentDate', '01.01.2019'))
        thickness = str(info.get('SliceThickness', '1'))
        number = str(info.get('ImagesNumber', '0'))

        v_layout = QVBoxLayout(self)
        v_layout.setAlignment(Qt.AlignCenter)

        info_label = QLabel(self)
        info_label.setText('%s\nT:%s N:%s' % (date, thickness, number))

        mini_label = QLabel()
        mini_label.setFixedHeight(self.maximumHeight() * 0.7)
        mini_label.setFixedWidth(self.maximumHeight() * 0.7)
        mini_label.setPixmap(self.array_to_pixmap(mini, mini_label))
        # mini_label

        v_layout.addWidget(info_label)
        v_layout.addWidget(mini_label)
        self.setLayout(v_layout)

    def array_to_pixmap(self, mini, owner):
        mini = Image.fromarray(mini).convert('RGB')
        mini = ImageQt.ImageQt(mini)
        return QPixmap.fromImage(mini).scaled(owner.width(), owner.height(),
                                              transformMode=Qt.SmoothTransformation)

    def focusInEvent(self, QFocusEvent):
        self.set_focus.emit(self.position)

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.LeftButton and QMouseEvent.modifiers() == Qt.NoModifier:
            self.setFocus()
