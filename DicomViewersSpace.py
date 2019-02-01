import logging
from threading import Thread

from PIL import Image, ImageQt
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QFrame, QLabel, QGridLayout, QDesktopWidget, QDialog, QPushButton, QComboBox, QCheckBox
from numpy import array, hstack, ndarray

from MAIA import MAIA

logging.basicConfig(level=logging.DEBUG)

"""
    Author: Ryabinin M.A
    Created: 20.11.2017
"""


class SlicesViewer(QLabel):
    """
        This class using for view 2d slice from slices set

        Parameters
        ----------
        _array_dicom_slices         :   ndarray
            3D Numpy array from slices image. Have 4 dimension if images have type RGB.

        _type_slice_position        :   string (Front,Side,Top)
            Type window for demonstration some type slices

        Attributes
        ---------
        _image_type                 :   string, (default=RGB) read more in pillow images convert type
            String for convert numpy to image with pillow image

        _power_array_dicom_slices   :   int, (default=100)
            The brightness setting for array DICOM. As np.array + power

        _current_number_slice       :   int, (default=100)
            Current number slice for demonstration image from array

        _max_number_slice           :   int, (default=0)
            The upper limit of the value _current_number_slice

        _image_scale_current        :   float, (default=0)
            Image scaling factor for correct construction of widgets

        _shape_widget_window        :   list, (default=[0,0,0])
            Shape for widget for correct construction of widgets
    """

    _array_dicom_slices = None
    _image_type = 'RGB'
    _power_array_dicom_slices = 100
    _contrast_array_dicom_slices = 1
    _type_slice_position = ''
    _current_number_slice = 1
    _max_number_slice = 1
    _image_scale_current = 0
    _shape_widget_window = [1, 1, 1]
    _text_number_slice = None
    _predict_cancer_point = array([])
    set_point_int_slice = pyqtSignal(list)
    start_mouse_position = None
    set_selection_cancer_points = pyqtSignal(ndarray)

    def __init__(self, type_slice_position, parent=None):
        """
        Initiates settings class
        :param type_slice_position: Type window for demonstration some type slices
        :param parent: Parent class
        """
        super().__init__()
        self._predict_cancer_point = array([])
        self._image_scale_current = array([1., 1.])
        self.start_mouse_position = [0, 0]
        self._selection_cancer_points = array([[None, None, None],
                                               [None, None, None]])
        self.volume_dialog = QDialog(self)
        self.volume_dialog.setWindowTitle('Nodule info')
        self.type_list = QComboBox()
        self.value_size = QLabel()
        self.confirmed_chech = QCheckBox()
        self.load_info_button = QPushButton('Save')
        self.setObjectName('SlicesViewer')
        self.setStyleSheet("QFrame#SlicesViewer { background-color: black }")
        self.setParent(parent)
        self._type_slice_position = type_slice_position
        logging.info("Window %s is initialised" % self._type_slice_position)
        self._initViewer()
        self._initWindowSize()
        self.init_volume_dialog()

    def _initViewer(self):
        """
        Initializing class widgets
        :return: None
        """

        self._text_number_slice = QLabel(self)
        self._text_number_slice.setObjectName("NumberSliceText")
        self._text_number_slice.setStyleSheet('QLabel#NumberSliceText {background-color: black}')
        self._text_number_slice.setText(MAIA.TextSetting.DicomViewerInitText % self._type_slice_position)

    def _initWindowSize(self):
        """
        Primary window size adjustment
        :return: None
        """

        height_window = self.parent().maximumHeight() - MAIA.WindowsSettings.SpacePointsBetween2DImages
        width_window = (self.parent().maximumWidth() - MAIA.WindowsSettings.SpacePointsBetween2DImages) // 2
        self.setMaximumSize(width_window, height_window)
        self._text_number_slice.setFixedSize(width_window, height_window)

    def setArrayDicomSlices(self, *args):
        """
        Setting a new array slices and rendering it
        :param array_dicom_slices: 3D Numpy array from slices image. Have 4 dimension if images have type RGB
        :return: None
        """
        self._clearSelectionPoints()
        self._array_dicom_slices = array(args)
        self._setMaxNumberSlice()
        self._setMaxWindowSize()
        self._renderArrayAsImage()

    def _setMaxNumberSlice(self):
        if self._type_slice_position == "front":
            self._max_number_slice = self._array_dicom_slices.shape[0]
        elif self._type_slice_position == "top":
            self._max_number_slice = self._array_dicom_slices.shape[1]
        elif self._type_slice_position == "side":
            self._max_number_slice = self._array_dicom_slices.shape[2]
        self._current_number_slice = self._max_number_slice // 2

    def _setMaxWindowSize(self):

        shape_slices_array = self._array_dicom_slices.shape[:3]

        min_size = min(self.parent().maximumHeight(),
                       self.parent().maximumWidth() // 2) - MAIA.WindowsSettings.SpacePointsBetween2DImages
        self._shape_widget_window[0] = min_size
        self._shape_widget_window[1] = min_size
        self._shape_widget_window[2] = min_size

        if self._type_slice_position == "front":
            self.setMaximumHeight(min_size)
            self.setMaximumWidth(min_size)
            self._image_scale_current[0] = min_size / shape_slices_array[2]
            self._image_scale_current[1] = min_size / shape_slices_array[1]
            # print(self._image_scale_current)
        elif self._type_slice_position == "top":
            self.setMaximumHeight(min_size)
            self.setMaximumWidth(min_size)
            self._image_scale_current[0] = min_size / shape_slices_array[2]
            self._image_scale_current[1] = min_size / shape_slices_array[0]
        elif self._type_slice_position == "side":
            self.setMaximumHeight(min_size)
            self.setMaximumWidth(min_size)
            self._image_scale_current[0] = min_size / shape_slices_array[0]
            self._image_scale_current[1] = min_size / shape_slices_array[1]
        self._text_number_slice.setFixedSize(50, 20)

    def setPowerArrayDicomSlices(self, pos):
        self._power_array_dicom_slices -= (self.start_mouse_position[1] - pos) // 2
        self.start_mouse_position[1] = pos
        self._renderArrayAsImage()

    def setPowerArray(self, power):
        self._power_array_dicom_slices = power
        self._renderArrayAsImage()

    def setContrastArrayDicomSlices(self, pos):
        self._contrast_array_dicom_slices -= (self.start_mouse_position[0] - pos) / 100
        self.start_mouse_position[0] = pos
        self._contrast_array_dicom_slices = max(0.1, self._contrast_array_dicom_slices)
        self._contrast_array_dicom_slices = min(12, self._contrast_array_dicom_slices)
        self._renderArrayAsImage()

    def setContrastArray(self, contrast):
        self._contrast_array_dicom_slices = contrast
        self._renderArrayAsImage()

    def _renderArrayAsImage(self):
        if self._array_dicom_slices is not None:
            if self._type_slice_position == "front":
                image_from_array = Image.fromarray(
                    (self._array_dicom_slices[self._current_number_slice, :,
                     :] // self._contrast_array_dicom_slices) + self._power_array_dicom_slices).convert(
                    self._image_type)
                image_to_qtimage = ImageQt.ImageQt(image_from_array)
                # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
                self.qtimage_pixmap = QPixmap.fromImage(image_to_qtimage).scaled(self._shape_widget_window[2],
                                                                                 self._shape_widget_window[1],
                                                                                 transformMode=Qt.SmoothTransformation)
                self.setPixmap(self.qtimage_pixmap)

            elif self._type_slice_position == "top":
                image_from_array = Image.fromarray(
                    (self._array_dicom_slices[:, self._current_number_slice,
                     :] // self._contrast_array_dicom_slices) + self._power_array_dicom_slices).convert(
                    self._image_type)
                image_to_qtimage = ImageQt.ImageQt(image_from_array)
                # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
                self.qtimage_pixmap = QPixmap.fromImage(image_to_qtimage).scaled(self._shape_widget_window[2],
                                                                                 self._shape_widget_window[0],
                                                                                 transformMode=Qt.SmoothTransformation)
                self.setPixmap(self.qtimage_pixmap)

            elif self._type_slice_position == "side":
                transpose_array = self._array_dicom_slices.transpose(1, 0, 2)
                image_from_array = Image.fromarray(
                    (transpose_array[:, :,
                     self._current_number_slice] // self._contrast_array_dicom_slices) + self._power_array_dicom_slices).convert(
                    self._image_type)
                image_to_qtimage = ImageQt.ImageQt(image_from_array)
                # noinspection PyCallByClass,PyTypeChecker,PyArgumentList
                self.qtimage_pixmap = QPixmap.fromImage(image_to_qtimage).scaled(self._shape_widget_window[0],
                                                                                 self._shape_widget_window[1],
                                                                                 transformMode=Qt.SmoothTransformation)
                self.setPixmap(self.qtimage_pixmap)

            self._text_number_slice.setText(MAIA.TextSetting.NumberSliceViewerTest % str(self._current_number_slice))

    def setCurrentNumberSlice(self, current_slice):
        if self._type_slice_position == "front":
            if self._current_number_slice != current_slice[2]:
                self._current_number_slice = current_slice[2]
                self._renderArrayAsImage()
        elif self._type_slice_position == "top":
            if self._current_number_slice != current_slice[0]:
                self._current_number_slice = current_slice[0]
                self._renderArrayAsImage()
        elif self._type_slice_position == "side":
            if self._current_number_slice != current_slice[1]:
                self._current_number_slice = current_slice[1]
                self._renderArrayAsImage()

    def mousePressEvent(self, QMouseEvent):
        if QMouseEvent.modifiers() == Qt.ControlModifier and QMouseEvent.button() == Qt.LeftButton:
            x = int(QMouseEvent.x() / self._image_scale_current[0])
            y = int(QMouseEvent.y() / self._image_scale_current[1])
            if self._type_slice_position == "front":
                # print([y, x, self._current_number_slice])
                self.set_point_int_slice.emit([y, x, self._current_number_slice])
            elif self._type_slice_position == "top":
                # print([self._current_number_slice, x, y])
                self.set_point_int_slice.emit([self._current_number_slice, x, y])
            elif self._type_slice_position == "side":
                # print([y, self._current_number_slice, x])
                self.set_point_int_slice.emit([y, self._current_number_slice, x])

        elif QMouseEvent.modifiers() == Qt.ShiftModifier and QMouseEvent.button() == Qt.LeftButton:
            x = int(QMouseEvent.x() / self._image_scale_current[0])
            y = int(QMouseEvent.y() / self._image_scale_current[1])
            self._setStartSelectionCancerPoint(x, y)
            self.update()

        elif QMouseEvent.button() == Qt.RightButton and QMouseEvent.modifiers() == Qt.ShiftModifier:
            self._clearSelectionPoints()
            self.update()
        elif QMouseEvent.button() == Qt.RightButton:
            self.add_selected_value(QMouseEvent)
        try:
            if QMouseEvent.button() == Qt.MiddleButton or QMouseEvent.button() == Qt.LeftButton:
                self.start_mouse_position = [int(QMouseEvent.x()), int(QMouseEvent.y())]
            else:
                self.start_mouse_position = [0, 0]
        except Exception as e:
            print(e)

    def mouseMoveEvent(self, QMouseEvent):
        if QMouseEvent.modifiers() == Qt.ShiftModifier and self._readyDrawSelectionCancer():
            x = int(QMouseEvent.x() / self._image_scale_current[0])
            y = int(QMouseEvent.y() / self._image_scale_current[1])
            self._setEndSelectionCancerPoint(x, y)
            self.update()
        elif self.start_mouse_position != [0, 0]:
            self.setPowerArrayDicomSlices(int(QMouseEvent.y()))
            self.setContrastArrayDicomSlices(int(QMouseEvent.x()))
            self.update()
            # print(self.start_mouse_position)
            # print(int(QMouseEvent.x()), int(QMouseEvent.y()))

    def paintEvent(self, event):
        super().paintEvent(event)
        if self._readyDrawSelectionCancer():
            cancer_selector = QPainter(self)
            cancer_selector.setPen(QPen(Qt.green, MAIA.ToolSettings.CancerSelectionPenSize))
            cancer_selector.drawRect(
                *(self._getSelectionCancerPoints() * hstack((self._image_scale_current, self._image_scale_current))))
            self.set_selection_cancer_points.emit(self._selection_cancer_points)
        if self._readyDrawPredictCancer():
            predict_selector = QPainter(self)
            predict_selector.setPen(QPen(Qt.red, MAIA.ToolSettings.CancerSelectionPenSize))
            for point in self._getPredictCancerPoints():
                predict_selector.drawRect(*(point * hstack((self._image_scale_current, self._image_scale_current))))

    def wheelEvent(self, QWheelEvent):
        if QWheelEvent.modifiers() == Qt.NoModifier:
            if 0 < self._current_number_slice + int(QWheelEvent.angleDelta().y() / 100) < self._max_number_slice:
                self._current_number_slice += int(QWheelEvent.angleDelta().y() / 100)
                self._renderArrayAsImage()
        elif QWheelEvent.modifiers() == Qt.ShiftModifier:
            if 0 < self._current_number_slice + int(QWheelEvent.angleDelta().y() / 10) < self._max_number_slice:
                self._current_number_slice += int(QWheelEvent.angleDelta().y() / 10)
                self._renderArrayAsImage()

    # def keyPressEvent(self, qKeyEvent):
    #     print(qKeyEvent.key())

    def _setStartSelectionCancerPoint(self, x, y):
        if self._type_slice_position == "front":
            if self._selection_cancer_points[0, 2] is None:
                self._selection_cancer_points[0] = [x, y, self._current_number_slice]
                self._selection_cancer_points[1] = [0, 0, 0]
            else:
                self._selection_cancer_points[0, :2] = [x, y]
                self._selection_cancer_points[1, :2] = [0, 0]
        elif self._type_slice_position == "top":
            if self._selection_cancer_points[0, 1] is None:
                self._selection_cancer_points[0] = [x, self._current_number_slice, y]
                self._selection_cancer_points[1] = [0, 0, 0]
            else:
                self._selection_cancer_points[0, [0, 2]] = [x, y]
                self._selection_cancer_points[1, [0, 2]] = [0, 0]
        elif self._type_slice_position == "side":
            if self._selection_cancer_points[0, 1] is None:
                self._selection_cancer_points[0] = [self._current_number_slice, y, x]
                self._selection_cancer_points[1] = [0, 0, 0]
            else:
                self._selection_cancer_points[0, 1:] = [y, x]
                self._selection_cancer_points[1, 1:] = [0, 0]

    def _setEndSelectionCancerPoint(self, x, y):
        if self._type_slice_position == "front":
            self._selection_cancer_points[1, :2] = array([x, y]) - self._selection_cancer_points[0, :2]
        elif self._type_slice_position == "top":
            self._selection_cancer_points[1, [0, 2]] = array([x, y]) - self._selection_cancer_points[0, [0, 2]]
        elif self._type_slice_position == "side":
            self._selection_cancer_points[1, 1:] = array([y, x]) - self._selection_cancer_points[0, 1:]
            # print(self._type_slice_position, self._selection_cancer_points[1])

    def _clearSelectionPoints(self):
        # print(self._selection_cancer_points)
        self._selection_cancer_points = array([[None, None, None],
                                               [None, None, None]])
        self.set_selection_cancer_points.emit(self._selection_cancer_points)

    def _readyDrawSelectionCancer(self):
        if (self._selection_cancer_points[0] != array([None, None, None])).all():
            return True
        else:
            return False

    def _getSelectionCancerPoints(self):
        if self._type_slice_position == "front":
            return hstack((self._selection_cancer_points[0, :2], self._selection_cancer_points[1, :2]))
        elif self._type_slice_position == "top":
            return hstack((self._selection_cancer_points[0, [0, 2]], self._selection_cancer_points[1, [0, 2]]))
        elif self._type_slice_position == "side":
            return hstack((self._selection_cancer_points[0, [2, 1]], self._selection_cancer_points[1, [2, 1]]))

    def setSelectionCancerPoints(self, *args):
        if (self._selection_cancer_points != array(*args)).any():
            self._selection_cancer_points = array(*args)
            self.update()

    def setPredictCancerPoint(self, array):
        self._predict_cancer_point = array
        # self.update()

    def _readyDrawPredictCancer(self):
        if len(self._predict_cancer_point):
            diap = []
            if self._type_slice_position == "front":
                diap = self._predict_cancer_point[:, :, 0]
            elif self._type_slice_position == "top":
                diap = self._predict_cancer_point[:, :, 1]
            elif self._type_slice_position == "side":
                diap = self._predict_cancer_point[:, :, 2]
            for d in diap:
                if d[1] >= self._current_number_slice >= d[0]:
                    return True
            return False
        else:
            return False

    def _getPredictCancerPoints(self):
        result = []
        for area in self._predict_cancer_point:
            ret = []
            if self._type_slice_position == "front":
                if area[0, 0] <= self._current_number_slice <= area[1, 0]:
                    ret = hstack((area[0, [2, 1]], area[1, [2, 1]]))
            elif self._type_slice_position == "top":
                if area[0, 1] <= self._current_number_slice <= area[1, 1]:
                    ret = hstack((area[0, [2, 0]], area[1, [2, 0]]))
            elif self._type_slice_position == "side":
                if area[0, 2] <= self._current_number_slice <= area[1, 2]:
                    ret = hstack((area[0, [0, 1]], area[1, [0, 1]]))
            if len(ret):
                ret[0] -= 5
                ret[1] -= 5
                ret[2] = 5 + ret[2] - ret[0]
                ret[3] = 5 + ret[3] - ret[1]
                result.append(ret)
        return result

    def init_volume_dialog(self):

        # self.load_info_button.clicked.connect(self.get_current_value)

        close_button = QPushButton('Cancel')
        close_button.clicked.connect(self.volume_dialog.close)

        label_type = QLabel()
        label_type.setText('Nodule type: ')

        label_size = QLabel()
        label_size.setText('Nodule volume in mm: ')

        label_confirmed = QLabel()
        label_confirmed.setText('Is confirmed nodule: ')

        self.value_size.setText('124')
        self.type_list.addItems([
            'A15.1 Lung tuberculosis (crop growth)',
            'A15.2 Lung tuberculosis (histologically confirmed)',
            'A15.3 Lung tuberculosis (inaccuratly confirmed)',
            'D13 Benign tumor',
            'D02 Carcinoma',
            'C34 Malignant formation of the lungs and bronchi',
            'J18 Pneumonia (without specifying the pathogen)',
            'J85.2 Lung abscess',
            'I26 Pulmonary embolism',
            'Other benign tumor',
            'D38 Neoplasms of uncertain nature',
            'Cancer metastases other localization'
        ])

        grid_layout = QGridLayout()
        grid_layout.addWidget(label_size, 0, 0)
        grid_layout.addWidget(label_type, 1, 0)
        grid_layout.addWidget(label_confirmed, 2, 0)

        grid_layout.addWidget(self.value_size, 0, 1, 1, 2)
        grid_layout.addWidget(self.type_list, 1, 1, 1, 2)
        grid_layout.addWidget(self.confirmed_chech, 2, 1, 1, 2)

        grid_layout.addWidget(self.load_info_button, 3, 1)
        grid_layout.addWidget(close_button, 3, 2)
        self.volume_dialog.setLayout(grid_layout)

    def add_selected_value(self, QMouseEvent):
        x = QMouseEvent.globalX() + 5
        y = QMouseEvent.globalY() + 50
        self.volume_dialog.setGeometry(x, y, 100, 100)
        self.volume_dialog.show()


class DicomViewersSpace(QFrame):
    """
        Class for combining the view of slices and patient data

        Attributes
        ---------
        _desktop                        :   QDesktopWidget
            Widget for calculating window sizes

        _widget_for_front_slices        :   SlicesViewer
            Widget for front slice

        _widget_for_top_slices          :   SlicesViewer
            Widget for top slice

        _widget_for_side_slices         :   SlicesViewer
            Widget for side slice

        _dicom_data_widget              :   QLabel
            Image scaling factor for correct construction of widgets
    """

    _desktop = None
    _widget_for_front_slices = None
    _widget_for_top_slices = None
    _widget_for_side_slices = None
    _dicom_data_widget = None
    _selection_space = array([[None, None, None],
                              [None, None, None]])

    def __init__(self, parent=None):
        """
        Initiates settings class
        :param parent: Parent class
        """
        super().__init__()
        self.setParent(parent)
        self.setObjectName("DicomViewerSpace")
        # self.setStyleSheet('QWidget#DicomViewerSpace { background-color: black }')
        logging.info("Windows for slices is initialised")
        self._initWindowSize()
        self._initSpace()

    def _initSpace(self):
        self.setFrameStyle(QFrame.Panel | QFrame.Plain)
        self.setLineWidth(4)
        self.setMidLineWidth(3)

        grid_layout = QGridLayout(self)
        self.setLayout(grid_layout)

        self._widget_for_front_slices = SlicesViewer("front", self)
        self._widget_for_front_slices.set_point_int_slice.connect(self._setCurrentSlice)

        # self._widget_for_top_slices = SlicesViewer("top", self)
        # self._widget_for_top_slices.set_point_int_slice.connect(self._setCurrentSlice)

        self._widget_for_side_slices = SlicesViewer("side", self)
        self._widget_for_side_slices.set_point_int_slice.connect(self._setCurrentSlice)

        grid_layout.addWidget(self._widget_for_front_slices, 0, 0, 2, 1)
        # grid_layout.addWidget(self._widget_for_top_slices, 0, 1, 2, 1)
        grid_layout.addWidget(self._widget_for_side_slices, 0, 1, 2, 1)

        self._widget_for_front_slices.set_selection_cancer_points.connect(self._setSelectionCancerPoints)
        # self._widget_for_top_slices.set_selection_cancer_points.connect(self._setSelectionCancerPoints)
        self._widget_for_side_slices.set_selection_cancer_points.connect(self._setSelectionCancerPoints)

    def _initWindowSize(self):
        self._desktop = QDesktopWidget()
        max_widget_height = self._desktop.availableGeometry(self._desktop.screenNumber(self)).height()
        max_widget_width = self._desktop.availableGeometry(self._desktop.screenNumber(self)).width()
        self.setFixedWidth(int(max_widget_width * MAIA.WindowsSettings.PercentWidthForWindowImageSlice))
        self.setFixedHeight(int(max_widget_height * MAIA.WindowsSettings.PercentHeightForViewers))

    def loadImagesFromDicom(self, array_dicom_slices):
        Thread(target=self._widget_for_front_slices.setArrayDicomSlices, args=array_dicom_slices).run()
        # Thread(target=self._widget_for_top_slices.setArrayDicomSlices, args=array_dicom_slices).run()
        Thread(target=self._widget_for_side_slices.setArrayDicomSlices, args=array_dicom_slices).run()

    def wheelEvent(self, QWheelEvent):
        pass
        # if int(QWheelEvent.modifiers()) == Qt.ControlModifier + Qt.ShiftModifier:
        #     self._widget_for_front_slices.setPowerArrayDicomSlices(QWheelEvent)
        #     # self._widget_for_top_slices.setPowerArrayDicomSlices(QWheelEvent)
        #     self._widget_for_side_slices.setPowerArrayDicomSlices(QWheelEvent)
        # elif int(QWheelEvent.modifiers()) == Qt.ControlModifier:
        #     self._widget_for_front_slices.setContrastArrayDicomSlices(QWheelEvent)
        #     # self._widget_for_top_slices.setPowerArrayDicomSlices(QWheelEvent)
        #     self._widget_for_side_slices.setContrastArrayDicomSlices(QWheelEvent)

    def mouseRightPressEvent(self, QMouseEvent):
        if QMouseEvent.button() == Qt.RightButton:
            print('Я родился')

    def set_lung_color_setting(self, key):
        if key == Qt.Key_0:
            power, contrast = 125, 1.3
        elif key == Qt.Key_1:
            power, contrast = 90, 12
        elif key == Qt.Key_2:
            power, contrast = 90, 1.3
        elif key == Qt.Key_3:
            power, contrast = 5, 2.5
        elif key == Qt.Key_4:
            power, contrast = 54, 6.1
        elif key == Qt.Key_5:
            power, contrast = -400, 0.1
        elif key == Qt.Key_6:
            power, contrast = 80, 1
        else:
            power, contrast = 190, 8

        self._widget_for_front_slices.setPowerArray(power)
        # self._widget_for_top_slices.setPowerArray(power)
        self._widget_for_side_slices.setPowerArray(power)

        self._widget_for_front_slices.setContrastArray(contrast)
        # self._widget_for_top_slices.setContrastArray(contrast)
        self._widget_for_side_slices.setContrastArray(contrast)

    def _setCurrentSlice(self, *args):
        Thread(target=self._widget_for_front_slices.setCurrentNumberSlice, args=args).run()
        # Thread(target=self._widget_for_top_slices.setCurrentNumberSlice, args=args).run()
        Thread(target=self._widget_for_side_slices.setCurrentNumberSlice, args=args).run()

    def _setSelectionCancerPoints(self, *args):
        Thread(target=self._widget_for_front_slices.setSelectionCancerPoints, args=args).run()
        # Thread(target=self._widget_for_top_slices.setSelectionCancerPoints, args=args).run()
        Thread(target=self._widget_for_side_slices.setSelectionCancerPoints, args=args).run()
        self._selection_space = args[0]

    def getSelectionSpace(self):
        return self._selection_space

    def setPredictCancerPoint(self, array):
        self._widget_for_front_slices.setPredictCancerPoint(array)
        self._widget_for_top_slices.setPredictCancerPoint(array)
        # self._widget_for_side_slices.setPredictCancerPoint(array)
