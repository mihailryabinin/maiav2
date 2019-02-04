from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QFrame, QLabel, QGridLayout, QDesktopWidget, QDialog, QPushButton, QComboBox, QCheckBox
import numpy as np
from PIL import Image, ImageQt
from Classes.Series import Series
from MAIA import MAIA


class SeriesViewer(QLabel):
    set_focus = pyqtSignal(QLabel)

    def __init__(self, parent, type_demonstration='side'):
        super().__init__()
        self.setParent(parent)
        self.init_widget()
        self.type_demonstration = type_demonstration

        self.image_scale = [1, 1]
        self.image = None
        self.current_slice = 0
        self.max_slice = 0
        self.image_contrast = 2
        self.image_light = 100
        self.series = Series()
        self.selected_coordinate = np.array([])
        self.predicted_coordinate = np.array([])

    def init_widget(self):
        self.setObjectName('SeriesViewer')
        self.setStyleSheet('QLabel#SeriesViewer { background-color: black }')
        self.setAlignment(Qt.AlignCenter)

    def load_series(self, series):
        try:
            if type(series) == Series:
                self.series = series
                self.image = self.series.get_image()
                self.update_viewer_settings()
            else:
                print('SeriesViewer.load_series not need type of series')
        except Exception as e:
            print(e)

    def render_image(self):
        try:
            if self.image is not None:
                if self.type_demonstration == "front":
                    try:
                        self.max_slice = self.image.shape[0]
                        image = (self.image[self.current_slice, :, :] // self.image_contrast) + self.image_light
                        image = Image.fromarray(image).convert('RGB')
                        image = ImageQt.ImageQt(image)
                        # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
                        image = QPixmap.fromImage(image).scaled(self.image_scale[0], self.image_scale[1],
                                                                transformMode=Qt.SmoothTransformation)
                        self.setPixmap(image)
                    except Exception as e:
                        print(e)

                elif self.type_demonstration == "top":
                    self.max_slice = self.image.shape[1]
                    image = (self.image[:, self.current_slice, :] // self.image_contrast) + self.image_light
                    image = Image.fromarray(image).convert('RGB')
                    image = ImageQt.ImageQt(image)
                    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
                    image = QPixmap.fromImage(image).scaled(self.image_scale[0], self.image_scale[1],
                                                            transformMode=Qt.SmoothTransformation)
                    self.setPixmap(image)

                elif self.type_demonstration == "side":
                    self.max_slice = self.image.shape[2]
                    image = self.image.transpose(1, 0, 2)
                    image = (image[:, :, self.current_slice] // self.image_contrast) + self.image_light
                    image = Image.fromarray(image).convert('RGB')
                    image = ImageQt.ImageQt(image)
                    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
                    image = QPixmap.fromImage(image).scaled(self.image_scale[0], self.image_scale[1],
                                                            transformMode=Qt.SmoothTransformation)
                    self.setPixmap(image)
        except Exception as e:
            print(e)

    def wheelEvent(self, QWheelEvent):
        if QWheelEvent.modifiers() == Qt.NoModifier:
            if 0 < self.current_slice + int(QWheelEvent.angleDelta().y() / 100) < self.max_slice:
                self.current_slice += int(QWheelEvent.angleDelta().y() / 100)
                self.render_image()
        elif QWheelEvent.modifiers() == Qt.ShiftModifier:
            if 0 < self.current_slice + int(QWheelEvent.angleDelta().y() / 10) < self.max_slice:
                self.current_slice += int(QWheelEvent.angleDelta().y() / 10)
                self.render_image()

    def focusInEvent(self, QFocusEvent):
        self.set_focus.emit(self)
        self.setStyleSheet('QLabel {background: rgb(20,20,20)}')

    def focusOutEvent(self, QFocusEvent):
        self.setStyleSheet('QLabel {background: black}')

    def mousePressEvent(self, QMouseEvent):
        try:
            if QMouseEvent.button() == Qt.LeftButton and QMouseEvent.modifiers() == Qt.NoModifier:
                self.setFocus()
        except Exception as e:
            print(e)

    def keyPressEvent(self, QKeyEvent):
        if Qt.Key_0 <= QKeyEvent.key() <= Qt.Key_7:
            self.set_image_settings(QKeyEvent.key())
        if Qt.Key_F == QKeyEvent.key():
            self.change_type_demonstration('front')
        if Qt.Key_S == QKeyEvent.key():
            self.change_type_demonstration('side')
        if Qt.Key_T == QKeyEvent.key():
            self.change_type_demonstration('top')

    def set_image_settings(self, key):
        light, contrast = 80, 5
        if key == Qt.Key_0:
            light, contrast = 125, 1.3
        elif key == Qt.Key_1:
            light, contrast = 90, 12
        elif key == Qt.Key_2:
            light, contrast = 90, 1.3
        elif key == Qt.Key_3:
            light, contrast = 5, 2.5
        elif key == Qt.Key_4:
            light, contrast = 54, 6.1
        elif key == Qt.Key_5:
            light, contrast = -400, 0.1
        elif key == Qt.Key_6:
            light, contrast = 80, 1
        elif key == Qt.Key_7:
            light, contrast = 190, 8

        self.image_light, self.image_contrast = light, contrast
        self.render_image()

    def update_viewer_settings(self):
        try:
            image_size = min(self.height() * MAIA.WindowsSettings.PercentVisibleImageDicomViewer,
                             self.width() * MAIA.WindowsSettings.PercentVisibleImageDicomViewer)
            self.image_scale = [image_size, image_size]
            if self.type_demonstration == "front":
                self.max_slice = self.image.shape[0]
            elif self.type_demonstration == "top":
                self.max_slice = self.image.shape[1]
            elif self.type_demonstration == "side":
                self.max_slice = self.image.shape[2]
            self.current_slice = self.max_slice // 2
            self.render_image()
        except Exception as e:
            print(e)

    def change_type_demonstration(self, new_type):
        if new_type in ['front', 'side', 'top']:
            try:
                self.type_demonstration = new_type
                self.update_viewer_settings()
            except Exception as e:
                print(e)
        else:
            print('Not need type demonstration for viewer')
