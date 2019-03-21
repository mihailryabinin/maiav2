from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QPen
from PyQt5.QtWidgets import QLabel, QMessageBox
import numpy as np
from PIL import Image, ImageQt
from classes.Series import Series
from AddVolumeDialog import AddVolumeDialog
from InfoVolumeDialog import InfoVolumeDialog
from MAIA import MAIA


class SeriesViewer(QLabel):
    set_focus = pyqtSignal(QLabel)
    choose_point = pyqtSignal(list, str)
    select_coordinate = pyqtSignal(np.ndarray, str)

    def __init__(self, parent, type_demonstration='front'):
        super().__init__()
        self.setParent(parent)
        self.init_widget()
        self.type_demonstration = type_demonstration
        self.show_all_contour = True

        self.image_scale = [1, 1]
        self.image = None
        self.current_slice = 0
        self.max_slice = 0
        self.image_contrast = 2
        self.image_light = 100
        self.series = Series()
        self.selected_coordinate = np.array([[None, None, None], [None, None, None]])
        self.coordinate_list = []
        self.predicted_coordinate = np.array([])
        self.series_id_owner = ''
        self.picture_window = [0, 0, 1, 1]
        self.volume_dialog = AddVolumeDialog(self.parent())
        self.volume_dialog.load_info_button.clicked.connect(self.add_volume_info)
        self.info_volume_dialog = InfoVolumeDialog(self.parent())
        self.info_volume_dialog.delete_volume_button.clicked.connect(self.delete_volume)

    def init_widget(self):
        self.setObjectName('SeriesViewer')
        self.setStyleSheet('QLabel#SeriesViewer { background-color: black }')
        self.setAlignment(Qt.AlignCenter)

    def load_series(self, series):
        try:
            if type(series) == Series:
                self.series = series
                self.series_id_owner = series.get_series_id()
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
        self.setStyleSheet('QLabel {background: rgb(30,30,30)}')

    def focusOutEvent(self, QFocusEvent):
        self.setStyleSheet('QLabel {background: black}')

    def mousePressEvent(self, QMouseEvent):
        try:
            if QMouseEvent.button() == Qt.LeftButton and QMouseEvent.modifiers() == Qt.NoModifier:
                self.setFocus()
            if QMouseEvent.button() == Qt.LeftButton and QMouseEvent.modifiers() == Qt.ControlModifier:
                self.choose_point_on_image(QMouseEvent.x(), QMouseEvent.y())
            if QMouseEvent.button() == Qt.LeftButton and QMouseEvent.modifiers() == Qt.ShiftModifier:
                self.set_start_select_point(QMouseEvent.x(), QMouseEvent.y())
            if QMouseEvent.button() == Qt.RightButton and QMouseEvent.modifiers() == Qt.ShiftModifier:
                self.selected_coordinate = np.array([[None, None, None], [None, None, None]])
                self.select_coordinate.emit(self.selected_coordinate, self.series_id_owner)
            if QMouseEvent.button() == Qt.RightButton and QMouseEvent.modifiers() == Qt.NoModifier:
                self.right_click(QMouseEvent)
        except Exception as e:
            print(e)

    def mouseMoveEvent(self, QMouseEvent):
        if QMouseEvent.modifiers() == Qt.ShiftModifier:
            self.set_stop_select_point(QMouseEvent.x(), QMouseEvent.y())
            if (self.selected_coordinate[1] != np.array([None, None, None])).all():
                self.select_coordinate.emit(self.selected_coordinate, self.series_id_owner)

    def keyPressEvent(self, QKeyEvent):
        # print(QKeyEvent.key())
        if Qt.Key_0 <= QKeyEvent.key() <= Qt.Key_7:
            self.set_image_settings(QKeyEvent.key())
        if Qt.Key_F == QKeyEvent.key() or QKeyEvent.key() == 1040:
            self.change_type_demonstration('front')
        if Qt.Key_S == QKeyEvent.key() or QKeyEvent.key() == 1067:
            self.change_type_demonstration('side')
        if Qt.Key_T == QKeyEvent.key() or QKeyEvent.key() == 1045:
            self.change_type_demonstration('top')

    def paintEvent(self, event):
        super().paintEvent(event)
        if (self.selected_coordinate != np.array([[None, None, None], [None, None, None]])).all():
            try:
                cancer_selector = QPainter(self)
                cancer_selector.setPen(QPen(Qt.green, MAIA.ToolSettings.CancerSelectionPenSize))
                cancer_selector.drawRect(*self.get_scale_selected_coordinate())
            except Exception as e:
                print(e, 'paint_event')
        if self.show_all_contour:
            try:
                contour_selector = QPainter(self)
                contour_selector.setPen(QPen(Qt.yellow, MAIA.ToolSettings.CancerSelectionPenSize))
                for contour in self.get_current_contour():
                    contour_selector.drawRect(*contour)
            except Exception as e:
                print(e, 'paint_event')

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

    def right_click(self, QMouseEvent):
        volume_info = self.get_volume_from_point(QMouseEvent.x(), QMouseEvent.y())
        if volume_info is not None:
            coordinate = self.return_real_point(QMouseEvent.x(), QMouseEvent.y())
            self.info_volume_dialog.update_selected_value(QMouseEvent, coordinate, volume_info)
        elif self.is_point_in_selected_area(QMouseEvent.x(), QMouseEvent.y()):
            volume_size = self.series.get_volume_size(np.sort(self.selected_coordinate, axis=0))
            self.volume_dialog.add_selected_value(QMouseEvent, volume_size)

    def update_viewer_settings(self):
        try:
            image_size = min(self.height() * MAIA.WindowsSettings.PercentVisibleImageDicomViewer,
                             self.width() * MAIA.WindowsSettings.PercentVisibleImageDicomViewer)
            self.image_scale = [image_size, image_size]
            self.picture_window = [(self.width() - image_size) // 2,
                                   (self.height() - image_size) // 2,
                                   ((self.width() - image_size) // 2) + image_size,
                                   ((self.height() - image_size) // 2) + image_size]
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
        if new_type in ['front', 'side', 'top'] and self.image is not None:
            try:
                self.type_demonstration = new_type
                self.update_viewer_settings()
            except Exception as e:
                print(e)
        else:
            print('Not need type demonstration for viewer')

    def is_similar_series_id(self, series_id):
        return self.series_id_owner == series_id

    def choose_point_on_image(self, x, y):
        if self.is_point_on_picture(x, y):
            coordinate = self.return_real_point(x, y)
            self.choose_point.emit(coordinate, self.series_id_owner)

    def is_point_on_picture(self, x, y):
        if self.image is not None:
            try:
                return x - self.picture_window[0] > 0 \
                       and y - self.picture_window[1] > 0 \
                       and x - self.picture_window[2] < -1 \
                       and y - self.picture_window[3] < -1
            except Exception as e:
                print(e, 'is_point_on_picture')
        else:
            return False

    def return_real_point(self, x, y):
        shape = self.image.shape
        x -= self.picture_window[0]
        y -= self.picture_window[1]
        try:
            if self.type_demonstration == "front":
                return [self.current_slice, int(y * shape[1] / self.pixmap().height()),
                        int(x * shape[2] / self.pixmap().width())]
            elif self.type_demonstration == "top":
                return [int(y * shape[0] / self.pixmap().height()), self.current_slice,
                        int(x * shape[2] / self.pixmap().width())]
            elif self.type_demonstration == "side":
                return [int(x * shape[0] / self.pixmap().width()),
                        int(y * shape[1] / self.pixmap().height()), self.current_slice
                        ]
        except Exception as e:
            print(e, 'return_real_point')

    def return_scale_point(self, coordinate):
        x, y = coordinate
        shape = self.image.shape
        try:
            if self.type_demonstration == "front":
                x, y = int(x / (shape[1] / self.pixmap().height())), int(y / (shape[2] / self.pixmap().width()))
                x += self.picture_window[1]
                y += self.picture_window[0]
            elif self.type_demonstration == "top":
                x, y = int(x / (shape[0] / self.pixmap().height())), int(y / (shape[2] / self.pixmap().width()))
                x += self.picture_window[1]
                y += self.picture_window[0]
            elif self.type_demonstration == "side":
                x, y = int(x / (shape[0] / self.pixmap().width())), int(y / (shape[1] / self.pixmap().height()))
                x += self.picture_window[0]
                y += self.picture_window[1]
            return int(x), int(y)
        except Exception as e:
            print(e, 'return_scale_point')

    def set_current_slice(self, slice_point, series_id):
        if self.series_id_owner == series_id:
            if self.type_demonstration == "front":
                self.current_slice = slice_point[0]
            elif self.type_demonstration == "top":
                self.current_slice = slice_point[1]
            elif self.type_demonstration == "side":
                self.current_slice = slice_point[2]
            self.render_image()

    def set_start_select_point(self, x, y):
        if self.is_point_on_picture(x, y):
            try:
                coordinate = np.array(self.return_real_point(x, y))
                if (self.selected_coordinate[0] == np.array([None, None, None])).all():
                    self.selected_coordinate[0] = coordinate
                else:
                    if self.type_demonstration == "front":
                        self.selected_coordinate[0, [1, 2]] = coordinate[[1, 2]]
                    elif self.type_demonstration == "top":
                        self.selected_coordinate[0, [0, 2]] = coordinate[[0, 2]]
                    elif self.type_demonstration == "side":
                        self.selected_coordinate[0, [0, 1]] = coordinate[[0, 1]]
            except Exception as e:
                print(e, 'set_start_select_point')

    def set_stop_select_point(self, x, y):
        if self.is_point_on_picture(x, y):
            try:
                coordinate = np.array(self.return_real_point(x, y))
                if (self.selected_coordinate[1] == np.array([None, None, None])).all():
                    self.selected_coordinate[1] = coordinate
                else:
                    if self.type_demonstration == "front":
                        self.selected_coordinate[1, [1, 2]] = coordinate[[1, 2]]
                    elif self.type_demonstration == "top":
                        self.selected_coordinate[1, [0, 2]] = coordinate[[0, 2]]
                    elif self.type_demonstration == "side":
                        self.selected_coordinate[1, [0, 1]] = coordinate[[0, 1]]
            except Exception as e:
                print(e, 'set_stop_select_point')

    def get_scale_selected_coordinate(self):
        try:
            coordinate = [0, 0, 0, 0]
            if self.type_demonstration == "front":
                coordinate = np.hstack((self.return_scale_point(self.selected_coordinate[0, [1, 2]]),
                                        self.return_scale_point(self.selected_coordinate[1, [1, 2]])))
                coordinate = coordinate[[1, 0, 3, 2]]
            elif self.type_demonstration == "top":
                coordinate = np.hstack((self.return_scale_point(self.selected_coordinate[0, [0, 2]]),
                                        self.return_scale_point(self.selected_coordinate[1, [0, 2]])))
                coordinate = coordinate[[1, 0, 3, 2]]
            elif self.type_demonstration == "side":
                coordinate = np.hstack((self.return_scale_point(self.selected_coordinate[0, [0, 1]]),
                                        self.return_scale_point(self.selected_coordinate[1, [0, 1]])))
            coordinate[[2, 3]] = coordinate[[2, 3]] - coordinate[[0, 1]]

            return coordinate
        except Exception as e:
            print(e, 'get_scale_selected_coordinate')

    def get_selected_coordinate(self):
        return self.selected_coordinate

    def set_selected_coordinate(self, coordinate, series_id):
        if self.series_id_owner == series_id:
            self.selected_coordinate = coordinate
            self.update()

    def is_point_in_selected_area(self, x, y):
        try:
            if self.is_point_on_picture(x, y) \
                    and (self.selected_coordinate != np.array([[None, None, None], [None, None, None]])).all():
                coordinate = self.return_real_point(x, y)
                selected_area = np.sort(self.selected_coordinate, axis=0)
                return selected_area[0, 0] <= coordinate[0] <= selected_area[1, 0] \
                       and selected_area[0, 1] <= coordinate[1] <= selected_area[1, 1] \
                       and selected_area[0, 2] <= coordinate[2] <= selected_area[1, 2]
            else:
                return False
        except Exception as e:
            print(e, 'is_point_in_selected_area')

    def add_volume_info(self):
        try:
            size_volume, type_volume, is_confirmed = self.volume_dialog.get_volume_info()
            coordinate = np.sort(self.selected_coordinate, axis=0)
            self.series.add_value(coordinate=coordinate, type_volume=type_volume, is_doctor=True,
                                  is_confirmed=is_confirmed, size=size_volume)
            QMessageBox.information(self.parent(), 'Volume is added',
                                    MAIA.TextSetting.InformationMessage % (type_volume + ' is saved'),
                                    QMessageBox.Ok)
            # self.coordinate_list.append(np.sort(self.selected_coordinate, axis=0))
            self.selected_coordinate = np.array([[None, None, None], [None, None, None]])
            self.select_coordinate.emit(self.selected_coordinate, self.series_id_owner)
            self.volume_dialog.close()
        except Exception as e:
            print(e, 'add_volume_info')

    def change_show_all(self):
        if self.show_all_contour:
            self.show_all_contour = False
        else:
            self.show_all_contour = True
        self.repaint()

    def get_current_contour(self):
        try:
            list_current_coordinate = []
            for coordinate in self.series.get_list_contour_from_doctor():
                current_coordinate = None
                if self.type_demonstration == "front":
                    if coordinate[0, 0] <= self.current_slice <= coordinate[1, 0]:
                        current_coordinate = np.hstack((self.return_scale_point(coordinate[0, [1, 2]]),
                                                        self.return_scale_point(coordinate[1, [1, 2]])))
                        current_coordinate = current_coordinate[[1, 0, 3, 2]]
                elif self.type_demonstration == "top":
                    if coordinate[0, 1] <= self.current_slice <= coordinate[1, 1]:
                        current_coordinate = np.hstack((self.return_scale_point(coordinate[0, [0, 2]]),
                                                        self.return_scale_point(coordinate[1, [0, 2]])))
                        current_coordinate = current_coordinate[[1, 0, 3, 2]]
                elif self.type_demonstration == "side":
                    if coordinate[0, 2] <= self.current_slice <= coordinate[1, 2]:
                        current_coordinate = np.hstack((self.return_scale_point(coordinate[0, [0, 1]]),
                                                        self.return_scale_point(coordinate[1, [0, 1]])))
                if current_coordinate is not None:
                    current_coordinate[[2, 3]] = current_coordinate[[2, 3]] - current_coordinate[[0, 1]]
                    list_current_coordinate.append(current_coordinate)

            return list_current_coordinate
        except Exception as e:
            print(e, 'get_current_contour')

    def get_volume_from_point(self, x, y):
        try:
            coordinate = self.return_real_point(x, y)
            return self.series.get_volume_from_point(*coordinate)
        except Exception as e:
            print(e, 'get_volume_from_point')

    def delete_volume(self):
        try:
            coordinate = self.info_volume_dialog.get_volume_coordinate()
            if coordinate is not None:
                self.series.delete_volume_from_point(*coordinate)
                self.info_volume_dialog.close()
                self.repaint()
        except Exception as e:
            print(e, 'delete_volume')

    def save_series(self):
        if self.series.save_series():
            QMessageBox.information(self.parent(), 'Save series',
                                    MAIA.TextSetting.InformationMessage % (
                                            self.series.get_series_info()['PatientName'] + ' is saved'),
                                    QMessageBox.Ok)
        else:
            QMessageBox.information(self.parent(), 'Save series',
                                    MAIA.TextSetting.InformationMessage % (
                                            self.series.get_series_info()['PatientName'] + ' is NOT saved'),
                                    QMessageBox.Ok)

    def get_file_to_send(self):
        if self.image is not None:
            try:
                return self.series.series_to_send_zip()
            except Exception as e:
                print(e, 'get_file_to_send')
                return None
