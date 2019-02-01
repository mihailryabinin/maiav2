import logging
from threading import Thread

from PIL import Image, ImageQt
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QLineEdit, QLabel, QGridLayout, QDesktopWidget
from numpy import array, hstack, ndarray

from MAIA import MAIA


class VolumeInfoCard(QLabel):
    info_params_edit = []

    def __init__(self):
        super().__init__()
        self.create_info_param()

    def create_info_param(self):
        info_params_name = ['param1', 'param2', 'param3',
                            'param4', 'param5', 'param6']
        for name in info_params_name:
            self.info_params_edit.append(Q)
