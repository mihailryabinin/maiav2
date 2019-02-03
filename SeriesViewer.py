from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QFrame, QLabel, QGridLayout, QDesktopWidget, QDialog, QPushButton, QComboBox, QCheckBox
import numpy as np
from PIL import Image, ImageQt
from Classes.Series import Series
from MAIA import MAIA


class SeriesViewer(QLabel):
    def __init__(self, parent, type_demonstration='front'):
        super().__init__()
        self.setParent(parent)
        self.init_widget()
        self.type_demonstration = type_demonstration

        self.image_scale = [1, 1]
        self.image = None
        self.current_slice = 0
        self.max_slice = 0
        self.image_contrast = 1
        self.image_light = 100
        self.series = Series()
        self.selected_coordinate = np.array([])
        self.predicted_coordinate = np.array([])

    def init_widget(self):
        self.setObjectName('SeriesViewer')
        self.setStyleSheet('QLabel#SeriesViewer { background-color: black }')
        self.setAlignment(Qt.AlignCenter)

        desktop = QDesktopWidget()
        print(desktop.availableGeometry(desktop.screenNumber(self)).height(),
              desktop.availableGeometry(desktop.screenNumber(self)).width()
              )

    def load_series(self, series):
        try:
            if type(series) == Series:
                self.series = series
                self.image = self.series.get_image()
                image_size = min(self.height() * MAIA.WindowsSettings.PercentVisibleImageDicomViewer,
                                 self.width() * MAIA.WindowsSettings.PercentVisibleImageDicomViewer)
                self.image_scale = [image_size, image_size]
                if self.type_demonstration == "front":
                    self.max_slice = self.image.shape[0]
                self.render_image()
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
                    image = QPixmap.fromImage(image)
                    image = image.scaled(self.image_scale[2], self.image_scale[0],
                                         transformMode=Qt.SmoothTransformation)
                    self.setPixmap(image)

                elif self.type_demonstration == "side":
                    self.max_slice = self.image.shape[2]
                    image = self.image.transpose(1, 0, 2)
                    image = (image[:, :, self.current_slice] // self.image_contrast) + self.image_light
                    image = Image.fromarray(image).convert('RGB')
                    image = ImageQt.ImageQt(image)
                    # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
                    image = QPixmap.fromImage(image)
                    image.scaled(self.image_scale[0],
                                 self.image_scale[1],
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
