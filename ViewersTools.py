from PyQt5.QtWidgets import QDesktopWidget, QLabel, QPushButton, QGridLayout, QLineEdit, QHBoxLayout
from PyQt5.QtGui import QFont, QPalette
from PyQt5.QtCore import Qt
from MAIA import MAIA


class ViewersTools(QLabel):
    test = None
    button_to_render = None
    set_render_space = None
    add_warning_space = None
    clear_all_warning_space = None
    density_space_l = None
    density_space_r = None
    density_warning_l = None
    density_warning_r = None
    save_cancer = None
    cancer_predict = None

    def __init__(self, parent=None):
        super().__init__()
        self.setParent(parent)
        self.setObjectName("series")
        self.setStyleSheet('QWidget#series { background-color: black }')
        self.initWindowSize()
        self.initViewer()

    def initViewer(self):
        self.setText(MAIA.TextSetting.DicomViewerInitText % self.objectName())

    def initWindowSize(self):
        desktop = QDesktopWidget()
        max_widget_height = desktop.availableGeometry(
            desktop.screenNumber(self)).height() * MAIA.WindowsSettings.PercentHeightForViewers
        max_widget_width = desktop.availableGeometry(
            desktop.screenNumber(self)).width() * MAIA.WindowsSettings.PercentToolsWidget
        self.setMaximumSize(max_widget_width, max_widget_height)

    def setTools(self):
        self.setText("")
        self.grid_layout = QGridLayout(self)
        self.setLayout(self.grid_layout)

        button_text_font = QFont()
        button_text_font.setPointSize(12)

        self.add_warning_space = QPushButton('Add cancer point', self)
        self.add_warning_space.setFont(button_text_font)

        self.clear_all_warning_space = QPushButton('Clear all cancer points', self)
        self.clear_all_warning_space.setFont(button_text_font)

        self.save_cancer = QPushButton('Save cancer', self)
        self.save_cancer.setFont(button_text_font)

        self.cancer_predict = QPushButton('Predict cancer', self)
        self.cancer_predict.setFont(button_text_font)

        self.grid_layout.setSpacing(0)

        self.grid_layout.addWidget(self.add_warning_space, 4, 0, 1, 2)
        self.grid_layout.addWidget(self.clear_all_warning_space, 7, 0, 1, 2)
        self.grid_layout.addWidget(self.save_cancer, 8, 0, 1, 2)
        self.grid_layout.addWidget(self.cancer_predict, 9, 0, 1, 2)

        self.update()

    def getDensitySpaceRender(self):
        return [self.density_space_l.text(), self.density_space_r.text()]

    def getDensityWarningSpace(self):
        return [self.density_warning_l.text(), self.density_warning_r.text()]
