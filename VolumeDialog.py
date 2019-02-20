from PyQt5.QtWidgets import QLabel, QPushButton, QDialog, QGridLayout, QCheckBox, QComboBox


class VolumeDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.setParent(parent)
        self.setWindowTitle('Nodule info')
        self.type_list = QComboBox()
        self.value_size = QLabel()
        self.confirmed_chech = QCheckBox()
        self.load_info_button = QPushButton('Save')
        self.init_volume_dialog()

    def init_volume_dialog(self):
        # self.load_info_button.clicked.connect(sel)

        close_button = QPushButton('Cancel')
        close_button.clicked.connect(self.close)

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
        self.setLayout(grid_layout)

    def add_selected_value(self, QMouseEvent):
        x = QMouseEvent.globalX() + 5
        y = QMouseEvent.globalY() + 50
        self.setGeometry(x, y, 100, 100)
        self.show()

    def get_volume_info(self):
        volume_type = self.type_list.currentText()
        confirmed = self.confirmed_chech.isChecked()
        return volume_type, confirmed
