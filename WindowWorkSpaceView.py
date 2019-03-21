from PyQt5.QtCore import Qt, QObject
from PyQt5.QtWidgets import QFrame, QGridLayout, QDesktopWidget, QHBoxLayout, QWidget, QVBoxLayout, QScrollArea, \
    QLabel, QMessageBox
from threading import Thread
from Aizimov import send_patient_to_predict, is_server_ready, get_patient_from_predict
from classes.Series import Series
from PatientMiniView import PatientMiniView
from SeriesViewer import SeriesViewer
from MAIA import MAIA


class WindowWorkSpaceView(QFrame):

    def __init__(self, parent=None):
        super().__init__()
        self.setParent(parent)
        self.setObjectName("WindowWorkSpace")
        self.init_window_size()

        self.list_series_viewer = []
        self.list_patient = []

        self.window_viewer_layout = QGridLayout()
        self.list_viewers = []
        self.current_viewer = None

        self.patient_viewer = QWidget()

        self.init_patient_viewer()
        self.init_space()
        self.set_window_viewer_layout()
        self.setVisible(False)

    def init_window_size(self):
        desktop = QDesktopWidget()
        max_widget_height = desktop.availableGeometry(desktop.screenNumber(self)).height() - 50
        max_widget_width = desktop.availableGeometry(desktop.screenNumber(self)).width()

        self.setMaximumWidth(int(max_widget_width))
        self.setMaximumHeight(int(max_widget_height))

    def init_patient_viewer(self):
        self.patient_viewer.setMaximumWidth(200)
        v_layout = QVBoxLayout()
        self.patient_viewer.setLayout(v_layout)
        self.patient_viewer.setStyleSheet("QWidget {background: rgb(100, 100, 100)}")

    def init_space(self):

        scroll_patient_list = QScrollArea(self)
        scroll_patient_list.setWidgetResizable(True)
        scroll_patient_list.setMaximumWidth(220)
        scroll_patient_list.setWidget(self.patient_viewer)
        scroll_patient_list.setStyleSheet("QScrollArea {background: rgb(50, 50, 50)}")

        h_layout = QHBoxLayout()
        h_layout.addWidget(scroll_patient_list)
        h_layout.addLayout(self.window_viewer_layout)
        self.setLayout(h_layout)

    def set_window_viewer_layout(self, number_windows=4):
        if number_windows == 1:
            series_viewer = SeriesViewer(self)
            self.window_viewer_layout.addWidget(series_viewer)
            #
        elif number_windows == 2:
            pass
        elif number_windows == 4:
            series_viewer = SeriesViewer(self)
            series_viewer.set_focus.connect(self.set_current_viewer)
            series_viewer.choose_point.connect(self.set_current_slice)
            series_viewer.select_coordinate.connect(self.set_selected_coordinate)
            self.window_viewer_layout.addWidget(series_viewer, 0, 0)
            self.list_viewers.append(series_viewer)

            series_viewer = SeriesViewer(self)
            series_viewer.set_focus.connect(self.set_current_viewer)
            series_viewer.choose_point.connect(self.set_current_slice)
            series_viewer.select_coordinate.connect(self.set_selected_coordinate)
            self.window_viewer_layout.addWidget(series_viewer, 0, 1)
            self.list_viewers.append(series_viewer)

            series_viewer = SeriesViewer(self)
            series_viewer.set_focus.connect(self.set_current_viewer)
            series_viewer.choose_point.connect(self.set_current_slice)
            series_viewer.select_coordinate.connect(self.set_selected_coordinate)
            self.window_viewer_layout.addWidget(series_viewer, 1, 0)
            self.list_viewers.append(series_viewer)

            series_viewer = SeriesViewer(self)
            series_viewer.set_focus.connect(self.set_current_viewer)
            series_viewer.choose_point.connect(self.set_current_slice)
            series_viewer.select_coordinate.connect(self.set_selected_coordinate)
            self.window_viewer_layout.addWidget(series_viewer, 1, 1)
            self.list_viewers.append(series_viewer)

    def load_patient(self, list_patient):
        self.setVisible(True)
        self.list_patient = list_patient
        self.add_mini()

    def add_mini(self):
        try:
            self.clear_mini()
            for pat, num_pat in zip(self.list_patient, range(len(self.list_patient))):
                list_series = pat.get_series()
                info_mini_widget = self.get_miniatures_info(list_series[0], len(list_series))
                self.patient_viewer.layout().addWidget(info_mini_widget)
                for ser, num_ser in zip(list_series, range(len(list_series))):
                    miniature_widget = PatientMiniView(self.patient_viewer,
                                                       ser.get_series_info(),
                                                       ser.get_miniature(),
                                                       [num_pat, num_ser])
                    miniature_widget.set_focus.connect(self.load_series_to_viewer)
                    self.patient_viewer.layout().addWidget(miniature_widget)
            self.patient_viewer.layout().addStretch()
        except Exception as e:
            print(e)

    def clear_mini(self):
        while self.patient_viewer.layout().count():
            child = self.patient_viewer.layout().takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def get_miniatures_info(self, first_series, len_series):
        info_widget = QLabel(self.patient_viewer)
        info_widget.setFixedWidth(self.patient_viewer.maximumWidth())
        info_widget.setStyleSheet('QLabel {background:white}')
        if type(first_series) == Series:
            patient_name = str(first_series.get_series_info().get('PatientName', 'No name'))
            patient_birth_date = str(first_series.get_series_info().get('PatientBirthDate', '01.01.1900'))
            info_widget.setText(
                MAIA.TextSetting.PatientInfoInPatientView % (patient_name, patient_birth_date, str(len_series)))
            return info_widget
        else:
            info_widget.setText('No name')
            return info_widget

    def load_series_to_viewer(self, position):
        try:
            if self.current_viewer is not None:
                pat, ser = position
                self.current_viewer.load_series(self.list_patient[pat].get_series()[ser])
        except Exception as e:
            print(e)

    def set_current_viewer(self, viewer):
        self.current_viewer = viewer

    def set_current_slice(self, slice_point, series_id):
        try:
            for widget in self.list_viewers:
                widget.set_current_slice(slice_point, series_id)
                # print(slice_point, series_id)
        except Exception as e:
            print(e, 'set_current_slice')

    def set_selected_coordinate(self, coordinate, series_id):
        try:
            for widget in self.list_viewers:
                widget.set_selected_coordinate(coordinate, series_id)
                # print(slice_point, series_id)
        except Exception as e:
            print(e, 'set_current_slice')

    def change_show_contour(self):
        try:
            for widget in self.list_viewers:
                widget.change_show_all()
        except Exception as e:
            print(e, 'change_show_contour')

    def save_series(self):
        try:
            if self.current_viewer is not None:
                self.current_viewer.save_series()
        except Exception as e:
            print(e, 'save_series')

    def send_series(self):
        try:
            if self.current_viewer is not None:
                if is_server_ready():
                    Thread(target=self.send_to_aizimov, args=()).start()
        except Exception as e:
            print(e, 'send_series_to_aizimov')

    def send_to_aizimov(self):
        result = self.current_viewer.get_file_to_send()
        if result is not None:
            send_patient_to_predict(result)

    def get_from_aizimov(self):
        list_series_id = []
        message = ['RESULTS:']
        try:
            for patient in self.list_patient:
                list_series = patient.get_series()
                for series in list_series:
                    list_series_id.append(series.get_series_id())
            if len(list_series_id):
                result = {'SeriesIDs': list_series_id}
                response = get_patient_from_predict(result)
                for patient in self.list_patient:
                    list_series = patient.get_series()
                    for series in list_series:
                        if series.get_series_id() in response.keys():
                            series_info = response[series.get_series_id()]
                            series.series_from_dict(series_info)
                            # print(series_info['Information']['PatientName'], len(series_info['Volumes']))
                            message.append('For %s found %s nodules' % (
                                str(series_info['Information']['PatientName']), str(len(series_info['Volumes']))))
                for widget in self.list_viewers:
                    widget.repaint()
            message = '<br>'.join(message)
            QMessageBox.information(self.parent(), 'Result from aizimov',
                                    MAIA.TextSetting.InformationMessage % message,
                                    QMessageBox.Ok)
        except Exception as e:
            print(e, 'get_from_aizimov')
