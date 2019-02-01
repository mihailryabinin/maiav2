import logging
from PyQt5.QtWidgets import QDialog, QTableWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QPushButton, QTableWidgetItem, \
    QMessageBox, QToolButton
from PyQt5.QtGui import QRegExpValidator, QIcon
from PyQt5.QtCore import QRegExp, Qt
from Classes.PacsDownload import PacsDownload


class PacsSettingView(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setParent(parent)
        self.setGeometry(400, 400, 500, 300)
        self.setWindowTitle('PACS setting')
        self.pacs_list_widget = QTableWidget(0, 4, self)
        self.pacs_list_widget.setSelectionBehavior(QTableWidget.SelectRows)

        self.ip_value = QLineEdit()
        self.ip_value.setPlaceholderText('IP')
        ip = QRegExp('[\.0-9]{7,15}')
        self.ip_value.setValidator(QRegExpValidator(ip))
        self.port_value = QLineEdit()
        self.port_value.setPlaceholderText('PORT')
        port = QRegExp('[0-9]{4,5}')
        self.port_value.setValidator(QRegExpValidator(port))
        self.title_value = QLineEdit()
        self.title_value.setPlaceholderText('TITLE')
        self.description_value = QLineEdit()
        self.description_value.setPlaceholderText('Description')
        self.pacs_downloder = PacsDownload()
        self.list_pacs = []
        self.init_ui()

    def init_ui(self):

        # self.pacs_downloder.add_pacs(conf_pacs)

        add_button = QToolButton()
        add_button.setIcon(QIcon('src/icon/add_pacs_button.ico'))
        add_button.clicked.connect(self.add_pacs)

        params_h_layout = QHBoxLayout()
        params_h_layout.addWidget(add_button)
        params_h_layout.addWidget(self.ip_value)
        params_h_layout.addWidget(self.port_value)
        params_h_layout.addWidget(self.title_value)
        params_h_layout.addWidget(self.description_value)

        vertical_layout = QVBoxLayout()
        vertical_layout.addLayout(params_h_layout)
        # vertical_layout.addStretch(1)

        self.pacs_list_widget.setHorizontalHeaderLabels([
            'PACS IP',
            'PACS PORT',
            'PACS TITLE',
            'PACS DESCRIPTION'
        ])
        self.pacs_list_widget.resizeColumnsToContents()
        self.pacs_list_widget.update()

        vertical_layout.addWidget(self.pacs_list_widget)

        # Test
        button_test = QPushButton('Clear')
        button_test.clicked.connect(self.delete_pacs)
        lay_out_test = QHBoxLayout()
        lay_out_test.addStretch(1)
        lay_out_test.addWidget(button_test)
        vertical_layout.addLayout(lay_out_test)

        self.setLayout(vertical_layout)

    def add_pacs(self):
        try:
            if self.ip_value.text() != '' and self.port_value.text() != '' and self.title_value.text() != '' and self.description_value.text() != '':
                ip = self.ip_value.text()
                port = self.port_value.text()
                title = self.title_value.text()
                descript = self.description_value.text()

                self.pacs_list_widget.insertRow(self.pacs_list_widget.rowCount())
                self.pacs_list_widget.setItem(self.pacs_list_widget.rowCount() - 1, 0, QTableWidgetItem(str(ip)))
                self.pacs_list_widget.setItem(self.pacs_list_widget.rowCount() - 1, 1, QTableWidgetItem(str(port)))
                self.pacs_list_widget.setItem(self.pacs_list_widget.rowCount() - 1, 2, QTableWidgetItem(str(title)))
                self.pacs_list_widget.setItem(self.pacs_list_widget.rowCount() - 1, 3, QTableWidgetItem(str(descript)))
                self.pacs_list_widget.resizeColumnsToContents()
                self.pacs_list_widget.resizeRowsToContents()

                self.list_pacs.append(str(descript))

                self.pacs_downloder.add_pacs(dict([
                    ('ip', str(ip)),
                    ('port', int(port)),
                    ('ae_title', str(title)),
                    ('description', str(descript))
                ]))
                self.ip_value.clear()
                self.port_value.clear()
                self.title_value.clear()
                self.description_value.clear()
        except Exception as e:
            print(e)

    def delete_pacs(self):
        # print(self.pacs_list_widget.currentRow())
        try:
            deleting_row = self.pacs_list_widget.currentRow()
            if deleting_row != -1:
                self.pacs_list_widget.removeRow(deleting_row)
                self.pacs_downloder.del_pacs(deleting_row)
        except Exception as e:
            print(e)

    def show_settings_dialog(self):
        try:
            self.show()
            self.setVisible(True)
        except Exception as e:
            print(e)

    def get_pacs_downloader(self):
        if len(self.pacs_downloder.list_pacs) > 0:
            return self.pacs_downloder
        else:
            return -1
