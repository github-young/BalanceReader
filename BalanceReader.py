import ctypes
import re
import sys
import time
from datetime import datetime

import serial
import serial.tools.list_ports
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QPalette, QIcon
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QTextEdit, QPushButton, QHBoxLayout, \
    QVBoxLayout, QFileDialog, QSpinBox, QProgressBar

my_app_id = 'HKUST.LiG.BalanceReader.v0.0.2'  # arbitrary string
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(my_app_id)
import resources


class BalanceReader(QWidget):
    def __init__(self):
        super().__init__()
        self.time_passed_in_second = 0
        self.interval_in_second = 0
        self.total_time_in_second = 0
        self.last_time = time.time()

        self.filename = ""

        icon = QIcon(":/icons/icon.ico")
        self.setWindowIcon(icon)
        self.initUI()

    def initUI(self):
        # Initialize the window and layout
        self.resize(400, 400)
        self.setWindowTitle('Balance Reader')
        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hbox3 = QHBoxLayout()
        hbox4 = QHBoxLayout()
        hbox5 = QHBoxLayout()
        hbox6 = QHBoxLayout()

        # Create the widgets
        suffix_width = 20
        self.port_label = QLabel('Port:')
        self.port_combo = QComboBox()
        self.port_suffix = QLabel('s')
        self.port_suffix.setFixedWidth(suffix_width)
        self.port_suffix.setPalette(QPalette(Qt.GlobalColor.transparent))  # set the label color to transparent
        self.baud_label = QLabel('Baud Rate:')
        self.baud_combo = QComboBox()
        self.baud_suffix = QLabel('s')
        self.baud_suffix.setFixedWidth(suffix_width)
        self.baud_suffix.setPalette(QPalette(Qt.GlobalColor.transparent))  # set the label color to transparent
        self.parity_label = QLabel('Parity:')
        self.parity_combo = QComboBox()
        self.parity_suffix = QLabel('s')
        self.parity_suffix.setFixedWidth(suffix_width)
        self.parity_suffix.setPalette(QPalette(Qt.GlobalColor.transparent))  # set the label color to transparent
        self.interval_label = QLabel('Interval:')
        self.interval_spin = QSpinBox()
        self.interval_suffix = QLabel('s')
        self.interval_suffix.setFixedWidth(suffix_width)
        self.duration_label = QLabel('Duration:')
        self.duration_spin = QSpinBox()
        self.duration_suffix = QLabel('min')
        self.duration_suffix.setFixedWidth(suffix_width)
        self.save_button = QPushButton('Set save path')
        self.start_button = QPushButton('Start')
        self.stop_button = QPushButton('Stop')
        self.text_edit = QTextEdit()
        self.text_edit.append("{}, {}, {}".format("Time/s", "Mass/g", "Timestamp"))
        self.text_edit.setReadOnly(True)
        self.line_label = QLabel("File saved as:")
        self.pbar = QProgressBar(self)

        # Add options to the combo boxes
        self.port_combo.addItems(self.get_serial_ports())
        self.port_combo.setCurrentIndex(self.port_combo.count() - 1)
        self.baud_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        self.parity_combo.addItems(['N', 'S', 'E', 'O', 'M'])

        # Set default values for the combo boxes and spin box
        self.baud_combo.setCurrentText('9600')
        self.parity_combo.setCurrentText('N')
        self.interval_spin.setRange(1, 3600)
        self.interval_spin.setValue(1)
        self.duration_spin.setRange(1, 10080)
        self.duration_spin.setValue(60)

        # Add the widgets to the layout
        hbox1.addWidget(self.port_label)
        hbox1.addWidget(self.port_combo)
        hbox1.addWidget(self.port_suffix)
        hbox2.addWidget(self.baud_label)
        hbox2.addWidget(self.baud_combo)
        hbox2.addWidget(self.baud_suffix)
        hbox3.addWidget(self.parity_label)
        hbox3.addWidget(self.parity_combo)
        hbox3.addWidget(self.parity_suffix)
        hbox4.addWidget(self.interval_label)
        hbox4.addWidget(self.interval_spin)
        hbox4.addWidget(self.interval_suffix)
        hbox6.addWidget(self.duration_label)
        hbox6.addWidget(self.duration_spin)
        hbox6.addWidget(self.duration_suffix)
        hbox5.addWidget(self.save_button)
        hbox5.addWidget(self.start_button)
        hbox5.addWidget(self.stop_button)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)
        vbox.addLayout(hbox6)
        vbox.addLayout(hbox5)
        vbox.addWidget(self.text_edit)
        vbox.addWidget(self.line_label)
        vbox.addWidget(self.pbar)

        # Set the layout for the window
        # vbox.addStretch()
        self.setLayout(vbox)

        # Connect the signals to the slots
        self.save_button.clicked.connect(self.set_save_path)
        self.start_button.clicked.connect(self.start_reading)
        self.stop_button.clicked.connect(self.stop_reading)

        # Initialize the timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_line_edit)

        # Show the window
        self.show()

    def get_serial_ports(self):
        # Returns a list of available serial ports
        ports = []
        for port in serial.tools.list_ports.comports():
            ports.append(port.device)
        return ports

    def start_reading(self):
        # Starts reading data from the selected serial port
        port = self.port_combo.currentText()
        baud = int(self.baud_combo.currentText())
        parity = self.parity_combo.currentText()
        interval = self.interval_spin.value() * 1000

        self.interval_in_second = int(self.interval_spin.value())
        self.total_time_in_second = int(self.duration_spin.value() * 60 / self.interval_in_second)

        # Initialize the serial connection
        self.ser = serial.Serial(port, baud, parity=parity, timeout=0)

        # Start the timer to read data at the specified interval
        self.timer.start(5)
        self.last_time = time.time()

        # Disable start button and enable stop button
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        # Toggle Edit access
        self.interval_spin.setReadOnly(True)
        self.duration_spin.setReadOnly(True)

    def stop_reading(self):
        # Stops reading data from the serial port
        self.timer.stop()
        self.ser.close()

        # Save to file
        self.save_data()

        # Clear progress bar
        self.pbar.setValue(0)

        # Disable stop button and enable start button
        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(True)

        # Toggle Edit access
        self.interval_spin.setReadOnly(False)
        self.duration_spin.setReadOnly(False)

    def update_line_edit(self):
        current_time = time.time()
        if current_time >= self.last_time + self.interval_in_second:
            self.read_data()
            # timestamp = datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]
            self.last_time += self.interval_in_second

    def read_data(self):
        # Reads data from the serial port and displays it in the text edit box
        try:
            ser_text_raw: str = self.ser.readline().decode("utf-8")
            timestamp = datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]
            ser_text = re.sub("[\r\nUS ]", '', ser_text_raw).split("g")[2]
            self.time_passed_in_second += self.interval_in_second
            if self.time_passed_in_second <= self.total_time_in_second:
                line = f'{self.time_passed_in_second:<10}, {ser_text:<10}, {timestamp}'
                self.text_edit.append(line)
                progress = int(100 * self.time_passed_in_second / self.total_time_in_second)
                self.pbar.setValue(progress)
            else:
                self.stop_button.click()
        except serial.SerialException:
            timestamp = datetime.now().strftime('%Y%m%d-%H:%M:%S.%f')[:-3]
            self.text_edit.append(f'{timestamp}: Error reading data from serial port')

    def set_save_path(self):
        # Set save path for output CSV file
        self.filename, _ = QFileDialog.getSaveFileName(self, 'Save Data', '', 'CSV Files (*.csv)')
        self.line_label.setText(f"File saved as: {self.filename}")

    def save_data(self):
        # Saves the data in the text edit box to a file
        if self.filename:
            with open(self.filename, 'w') as f:
                f.write(self.text_edit.toPlainText().replace(" ", ""))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    serial_reader = BalanceReader()
    sys.exit(app.exec())