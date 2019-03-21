from PyQt5.QtWidgets import QLabel, QPushButton, QDialog, QGridLayout, QCheckBox, QComboBox


class InfoVolumeDialog(QDialog):

    def __init__(self, parent):
        super().__init__(parent)
        self.setParent(parent)
        self.setWindowTitle('Nodule info')
        self.coordinate = None
        self.volume_size = QLabel()
        self.volume_type = QLabel()
        self.probability = QLabel()
        self.is_doctor = QLabel()
        self.confirmed_check = QLabel()
        self.delete_volume_button = QPushButton('Delete')
        self.init_volume_dialog()

    def init_volume_dialog(self):
        # self.load_info_button.clicked.connect(sel)

        close_button = QPushButton('Cancel')
        close_button.clicked.connect(self.close)

        label_size = QLabel()
        label_size.setText('Nodule volume in mm: ')

        label_type = QLabel()
        label_type.setText('Nodule type: ')

        label_probability = QLabel()
        label_probability.setText('Probability: ')

        label_is_doctor = QLabel()
        label_is_doctor.setText('From doctor: ')

        label_confirmed = QLabel()
        label_confirmed.setText('Is confirmed nodule: ')

        grid_layout = QGridLayout()
        grid_layout.addWidget(label_size, 0, 0)
        grid_layout.addWidget(label_type, 1, 0)
        grid_layout.addWidget(label_probability, 2, 0)
        grid_layout.addWidget(label_is_doctor, 3, 0)
        grid_layout.addWidget(label_confirmed, 4, 0)

        grid_layout.addWidget(self.volume_size, 0, 1, 1, 2)
        grid_layout.addWidget(self.volume_type, 1, 1, 1, 2)
        grid_layout.addWidget(self.probability, 2, 1, 1, 2)
        grid_layout.addWidget(self.is_doctor, 3, 1, 1, 2)
        grid_layout.addWidget(self.confirmed_check, 4, 1, 1, 2)

        grid_layout.addWidget(self.delete_volume_button, 5, 1)
        grid_layout.addWidget(close_button, 5, 2)
        self.setLayout(grid_layout)

    def update_selected_value(self, QMouseEvent, coordinate, info):
        self.coordinate = coordinate
        self.update_info(info)
        x = QMouseEvent.globalX() + 5
        y = QMouseEvent.globalY() + 50
        self.setGeometry(x, y, 100, 100)
        self.show()

    def update_info(self, info):
        self.volume_size.setText('0' if info['volume_size'] is None else str(info['volume_size']))
        self.volume_type.setText(info['volume_type'])
        self.probability.setText('0' if info['probability'] is None else str(int(100 * info['probability'])) + '%')
        self.is_doctor.setText('Yes' if info['is_doctor'] else 'No')
        self.confirmed_check.setText('Yes' if info['is_confirmed'] else 'No')

    def get_volume_coordinate(self):
        return self.coordinate
