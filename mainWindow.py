import os
import logging
from imageSegmentation import ImageSegmentation
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QFileDialog, QAction, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, Qt
import DicomViewersSpace
from MAIA import MAIA
from PacsDownloaderView import PacsDownloadViewer
from ViewersTools import ViewersTools

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

        # Setup menu_bar
        # menu_bar = self.menuBar()
        # file_menu_bar = menu_bar.addMenu("File")
        # file_menu_bar.addAction(open_file)

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

        main_widget = QWidget(self)

        # Dicom widgets
        self.ctwidget = DicomViewersSpace.DicomViewersSpace(self)

        self.viewertool = ViewersTools(self)

        # Set dicom wigets on main widgets
        self.layout_main_windows = QHBoxLayout(self)
        main_widget.setLayout(self.layout_main_windows)
        self.layout_main_windows.addWidget(self.viewertool)
        self.layout_main_windows.addWidget(self.ctwidget)

        self.setCentralWidget(main_widget)
        self.showMaximized()

    def showLoadDICOMDialog(self):
        try:
            path_to_dicom = QFileDialog.getExistingDirectory(self, 'Open DICOM directory')
            self.path_to_dicom = path_to_dicom
            ok = 110
            if path_to_dicom != '':
                all_files = os.listdir(path_to_dicom)

                for file in all_files:
                    if file.find('.dcm') > 0:
                        ok += 1
            else:
                return -1
            if ok > 10:
                self.image = ImageSegmentation(self.path_to_dicom)
                # SclicesView
                self.ctwidget.loadImagesFromDicom(self.image.getArrayDicomFromPath())
                # self.ctwidget.loadDicomMetaData(self.image.getDicomMetaData())

                # ViewTools
                # self.viewertool.setTools()
                # self.viewertool.add_warning_space.clicked.connect(self.setWarningSpace)
                # self.viewertool.clear_all_warning_space.clicked.connect(self.clearAllWarningSpace)
                # self.viewertool.save_cancer.clicked.connect(self.saveCancer)
                # self.viewertool.cancer_predict.clicked.connect(self.predictCancer)
            else:
                QMessageBox.information(self, 'Download DICOM',
                                        MAIA.TextSetting.InformationMessage % 'DICOM files not found or too few',
                                        QMessageBox.Ok)
        except Exception as e:
            print(e)

    def setWarningSpace(self):
        self.volume_object.setListWarningSpace(self.ctwidget.getSelectionSpace())
        self.volume_object.setDensityWarningSpace(self.viewertool.getDensityWarningSpace())
        QMessageBox.information(self, 'Cancer point', MAIA.TextSetting.InformationMessage % 'Cancer point added',
                                QMessageBox.Ok)

    def clearAllWarningSpace(self):
        self.volume_object.clearAllWarningSpace()
        QMessageBox.information(self, 'Clear cancer points',
                                MAIA.TextSetting.InformationMessage % 'All cancer points are deleted',
                                QMessageBox.Ok)

    def saveCancer(self):
        self.volume_object.saveCancer()
        QMessageBox.information(self, 'Save cancer',
                                MAIA.TextSetting.InformationMessage % 'Cancer saved',
                                QMessageBox.Ok)

    def predictCancer(self):
        # print(self.path_to_dicom[0])
        QMessageBox.information(self, 'Predict cancer',
                                MAIA.TextSetting.InformationMessage % 'Predict OK',
                                QMessageBox.Ok)

    def keyPressEvent(self, e):
        if Qt.Key_0 <= e.key() <= Qt.Key_7:
            self.ctwidget.set_lung_color_setting(e.key())
