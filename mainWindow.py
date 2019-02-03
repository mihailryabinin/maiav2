import os
import logging
from imageSegmentation import ImageSegmentation
from PyQt5.QtWidgets import QMainWindow, QHBoxLayout, QFileDialog, QAction, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize
from MAIA import MAIA
from DownloadViews.PacsDownloaderView import PacsDownloadViewer
from Classes.FolderDownload import FolderDownload
from WindowWorkSpaceView import WindowWorkSpaceView

logging.basicConfig(level=logging.DEBUG)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setObjectName("MainWindow")
        self.initWindow()

    def initWindow(self):
        # Setup main window properties
        self.setWindowTitle('MAIA - Medical Artificial Intelligence Assistant')
        self.setWindowIcon(QIcon('./src/icon/mainiconii.png'))

        # Open DICOM series
        open_file = QAction(QIcon('src/icon/opendicom.ico'), 'Open', self)
        open_file.setShortcut('Ctrl+O')
        open_file.setStatusTip('Open new File')
        open_file.triggered.connect(self.showLoadDICOMDialog)

        download_from_pacs = QAction(QIcon('src/icon/downloaddicomfrompacs.png'), 'Download from PACS', self)
        download_from_pacs.setShortcut('Ctrl+P')
        download_from_pacs.setStatusTip('Download patients from PACS')
        pacs_downloader = PacsDownloadViewer(self)
        download_from_pacs.triggered.connect(pacs_downloader.show_search_dialog)

        # Setup toolbar
        open_toolbar = self.addToolBar('DICOM')
        open_toolbar.addAction(open_file)
        open_toolbar.addAction(download_from_pacs)
        open_toolbar.setIconSize(QSize(32, 32))
        open_toolbar.setStyleSheet("QToolBar {background: rgb(100, 100, 100)}")
        #
        add_volume = QAction(QIcon('src/icon/addvolume.ico'), 'Add volume', self)
        add_volume.setStatusTip('Add new volume')

        patient_info = QAction(QIcon('src/icon/patientinfo.ico'), 'Add patient info', self)
        patient_info.setStatusTip('Add patient info')

        ai_toolbar = self.addToolBar('AI teacher')
        ai_toolbar.addAction(add_volume)
        ai_toolbar.addAction(patient_info)
        # print(toolbar.iconSize())
        ai_toolbar.setIconSize(QSize(32, 32))
        ai_toolbar.setStyleSheet("QToolBar {background: rgb(100, 100, 100)}")
        #
        send_to_ai = QAction(QIcon('src/icon/sendtoai.ico'), 'Send to AIzimov', self)
        send_to_ai.setStatusTip('Send to AIzimov')
        az_toolbar = self.addToolBar('AI')
        az_toolbar.addAction(send_to_ai)
        az_toolbar.setIconSize(QSize(32, 32))
        az_toolbar.setStyleSheet("QToolBar {background: rgb(100, 100, 100)}")

        self.setStyleSheet('QMainWindow {border-image: url(src/background/main_window_background.png)}')

        # Dicom widgets
        self.ctwidget = WindowWorkSpaceView(self)
        # self.ctwidget = DicomViewersSpace.DicomViewersSpace(self)

        # Set dicom wigets on main widgets
        self.layout_main_windows = QHBoxLayout(self)
        self.layout_main_windows.addWidget(self.ctwidget)

        self.setCentralWidget(self.ctwidget)
        self.showMaximized()

    def showLoadDICOMDialog(self):
        try:
            path_to_dicom = QFileDialog.getExistingDirectory(self, 'Open DICOM directory')
            if path_to_dicom != '':
                folder_downloader = FolderDownload(path_to_dicom)
                self.ctwidget.load_patient(folder_downloader.get_patient_from_folders())
                pass

        except Exception as e:
            print(e)
