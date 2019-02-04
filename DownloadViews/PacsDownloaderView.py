from PyQt5.QtWidgets import QToolButton, QComboBox, QDialog, QTableWidget, QVBoxLayout, QHBoxLayout, QGridLayout, \
    QLineEdit, QPushButton, QTableWidgetItem, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
from Classes.PacsDownload import PacsDownload
from DownloadViews.PacsSettingView import PacsSettingView


class PacsDownloadViewer(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setParent(parent)
        # self.setGeometry(300, 300, 900, 500)
        self.setMinimumWidth(800)
        self.setMinimumHeight(400)
        self.setWindowTitle('PACS')
        self.patient_list_widget = QTableWidget(0, 8, self)
        self.patient_list_widget.setSelectionBehavior(QTableWidget.SelectRows)
        self.patient_list_widget.setSelectionMode(QTableWidget.SingleSelection)
        self.list_param_search_name = QComboBox()
        self.param_search_value = QLineEdit()
        self.translit_dict = dict([
            ('Patient name', 'PatientName'),
            ('Patient ID', 'PatientID'),
            ('Accession number', 'AccessionNumber'),
            ('Study description', 'StudyDescription'),
            ('Referring physician', 'ReferringPhysicianName'),
            # ('Performing physician','AccessionNumber'),
            # ('Reading physician','ReferringPhysicianName'),
            ('Institute name', 'InstitutionName')
        ])
        self.pacs_setting_view = PacsSettingView(self)
        self.init_ui()

    def init_ui(self):
        setting_pacs_button = QToolButton()
        setting_pacs_button.setIcon(QIcon('src/icon/settings_pacs_button.ico'))
        setting_pacs_button.clicked.connect(self.pacs_setting_view.show)

        pacs_list = QComboBox()  # get list of pacs
        pacs_list.addItems(['All PACS location'])

        modalities_list = QComboBox()  # get list modalities
        modalities_list.addItems(['All modalities'])

        self.list_param_search_name.addItems([
            'Patient name',
            'Patient ID',
            'Accession number',
            'Study description',
            'Referring physician',
            # 'Performing physician',
            # 'Reading physician',
            'Institute name'])

        search_button = QPushButton('Search')
        search_button.clicked.connect(self.start_search)
        clear_button = QPushButton('Clear')
        clear_button.clicked.connect(self.param_search_value.clear)
        # clear_button.clicked.connect(self.patient_list_widget.setRowCount)

        settings_grid_layout = QGridLayout()
        settings_grid_layout.addWidget(setting_pacs_button, 0, 0)
        settings_grid_layout.addWidget(pacs_list, 0, 1)
        settings_grid_layout.addWidget(modalities_list, 0, 2)
        settings_grid_layout.addWidget(self.list_param_search_name, 1, 0, 1, 2)
        settings_grid_layout.addWidget(self.param_search_value, 1, 2, 1, 3)
        settings_grid_layout.addWidget(search_button, 1, 5)
        settings_grid_layout.addWidget(clear_button, 1, 6)

        vertical_layout = QVBoxLayout()
        vertical_layout.addLayout(settings_grid_layout)
        # vertical_layout.addStretch(1)

        self.patient_list_widget.setHorizontalHeaderLabels([
            'Study date',
            'Patient name',
            'Birth date',
            'Patient ID',
            'Study description',
            'Accession number ',
            'Referring physician',
            # 'Physicians reading',
            'Institution name',
            # 'Performing physician'
        ])
        self.patient_list_widget.resizeColumnsToContents()
        self.patient_list_widget.update()

        vertical_layout.addWidget(self.patient_list_widget)

        # Test
        button_test = QPushButton('Load')
        lay_out_test = QHBoxLayout()
        lay_out_test.addStretch(1)
        lay_out_test.addWidget(button_test)
        vertical_layout.addLayout(lay_out_test)

        self.setLayout(vertical_layout)

    def start_search(self):
        try:
            # Table
            downloder = self.pacs_setting_view.get_pacs_downloader()
            if type(downloder) is PacsDownload:
                param_name = self.translit_dict[self.list_param_search_name.currentText()]
                param_value = self.param_search_value.text()
                if param_value == '':
                    message_overlow = QMessageBox.warning(self, 'Warning',
                                                          'Отсутствуют фильтры поиска, это может занять время',
                                                          QMessageBox.Ok | QMessageBox.Cancel)
                    if message_overlow != QMessageBox.Ok:
                        return -1
                result = downloder.find_in_pacs({param_name: param_value})
                if type(result) is list:
                    self.patient_list_widget.setRowCount(0)
                    self.download_list_patient(result[0])
            else:
                QMessageBox.information(self, 'Info',
                                        'Не добавлен ни один сервер PACS',
                                        QMessageBox.Ok)
        except Exception as e:
            print(e)

    def download_list_patient(self, result):
        try:
            for patient in result:
                self.patient_list_widget.insertRow(self.patient_list_widget.rowCount())
                items = self.generate_items(patient)
                for i in range(len(self.patient_list_widget.horizontalHeader())):
                    self.patient_list_widget.setItem(self.patient_list_widget.rowCount() - 1, i, items[i])

            self.patient_list_widget.resizeColumnsToContents()
            self.patient_list_widget.resizeRowsToContents()
            self.patient_list_widget.update()
        except Exception as e:
            print(e)

    def generate_items(self, patient):
        study_data = str(patient.StudyDate)
        study_data = '-'.join([study_data[6:], study_data[4:6], study_data[:4]])
        list_param = [
            study_data,
            patient.PatientName,
            patient.PatientBirthDate,
            patient.PatientID,
            patient.StudyDescription,
            patient.AccessionNumber,
            patient.ReferringPhysicianName,
            # '',
            patient[0x00080080].value,
            # ''
        ]
        # print(list_param)
        items = []
        for i in range(len(self.patient_list_widget.horizontalHeader())):
            item = QTableWidgetItem()
            item.setFlags(item.flags() | ~Qt.ItemIsEditable)  # not work
            item.setText(str(list_param[i]))
            items.append(item)
        return items

    def show_search_dialog(self):
        try:
            self.show()
            self.setVisible(True)
        except Exception as e:
            print(e)
