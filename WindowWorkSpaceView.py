from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QGridLayout, QDesktopWidget, QHBoxLayout, QWidget

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
        self.patient_viewer = QWidget(self)
        self.patient_viewer.setStyleSheet("QWidget { background-color: black }")

        self.init_patient_viewer()
        self.init_space()
        # self.set_window_viewer_layout()

    def init_window_size(self):
        desktop = QDesktopWidget()
        max_widget_height = desktop.availableGeometry(desktop.screenNumber(self)).height()
        max_widget_width = desktop.availableGeometry(desktop.screenNumber(self)).width()

        self.setMaximumWidth(int(max_widget_width))
        self.setMaximumHeight(int(max_widget_height))

    def init_patient_viewer(self):
        self.patient_viewer.setMaximumWidth(200)

    def init_space(self):

        h_layout = QHBoxLayout()
        h_layout.addWidget(self.patient_viewer)
        h_layout.addLayout(self.window_viewer_layout)
        self.setLayout(h_layout)

    def set_window_viewer_layout(self, number_windows=4):
        if number_windows == 1:
            series_viewer = SeriesViewer(self)
            print(series_viewer.baseSize().height())
            self.window_viewer_layout.addWidget(series_viewer)
            series_viewer.load_series(self.list_patient[0].get_series()[0])
        elif number_windows == 2:
            series_viewer = SeriesViewer(self)
            self.window_viewer_layout.addWidget(series_viewer, 0, 0)
            series_viewer.load_series(self.list_patient[0].get_series()[0])
            series_viewer = SeriesViewer(self)
            self.window_viewer_layout.addWidget(series_viewer, 0, 1)
            series_viewer.load_series(self.list_patient[0].get_series()[0])
        elif number_windows == 4:
            series_viewer = SeriesViewer(self)
            self.window_viewer_layout.addWidget(series_viewer, 0, 0)
            series_viewer.load_series(self.list_patient[0].get_series()[0])
            series_viewer = SeriesViewer(self)
            self.window_viewer_layout.addWidget(series_viewer, 0, 1)
            series_viewer.load_series(self.list_patient[0].get_series()[0])
            series_viewer = SeriesViewer(self)
            self.window_viewer_layout.addWidget(series_viewer, 1, 0)
            series_viewer.load_series(self.list_patient[0].get_series()[0])
            series_viewer = SeriesViewer(self)
            self.window_viewer_layout.addWidget(series_viewer, 1, 1)
            series_viewer.load_series(self.list_patient[0].get_series()[0])
            pass

    def load_patient(self, list_patient):
        self.list_patient = list_patient
        self.set_window_viewer_layout()
