from PyQt5.QtCore import Qt, QObject
from PyQt5.QtWidgets import QFrame, QGridLayout, QDesktopWidget, QHBoxLayout, QWidget, QVBoxLayout, QScrollArea, QLabel

from Classes.Series import Series
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
            self.window_viewer_layout.addWidget(series_viewer, 0, 0)
            series_viewer = SeriesViewer(self)
            series_viewer.set_focus.connect(self.set_current_viewer)
            self.window_viewer_layout.addWidget(series_viewer, 0, 1)
            series_viewer = SeriesViewer(self)
            series_viewer.set_focus.connect(self.set_current_viewer)
            self.window_viewer_layout.addWidget(series_viewer, 1, 0)
            series_viewer = SeriesViewer(self)
            series_viewer.set_focus.connect(self.set_current_viewer)
            self.window_viewer_layout.addWidget(series_viewer, 1, 1)

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
                    miniature_widget.set_focus.connect(self.load_serie_to_viewer)
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

    def load_serie_to_viewer(self, position):
        try:
            if self.current_viewer is not None:
                pat, ser = position
                self.current_viewer.load_series(self.list_patient[pat].get_series()[ser])
        except Exception as e:
            print(e)

    def set_current_viewer(self, viewer):
        self.current_viewer = viewer
        print(str(viewer))

    def change_series_viewer_to_front(self):
        self.current_viewer.change_type_demonstration('front')
