import sys
import serial
import serial.tools.list_ports
import datetime
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QPalette
from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QComboBox, QTextEdit, QPushButton, QHBoxLayout, QVBoxLayout, QFileDialog, QSpinBox


class SerialReader(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Initialize the window and layout
        self.setGeometry(100, 100, 500, 500)
        self.setWindowTitle('Serial Reader')
        vbox = QVBoxLayout()
        hbox1 = QHBoxLayout()
        hbox2 = QHBoxLayout()
        hbox3 = QHBoxLayout()
        hbox4 = QHBoxLayout()
        hbox5 = QHBoxLayout()

        # Create the widgets
        self.port_label = QLabel('Port:')
        self.port_combo = QComboBox()
        self.port_suffix = QLabel('s')
        self.port_suffix.setFixedWidth(10)
        self.port_suffix.setPalette(QPalette(Qt.GlobalColor.transparent)) # set the label color to transparent
        self.baud_label = QLabel('Baud Rate:')
        self.baud_combo = QComboBox()
        self.baud_suffix = QLabel('s')
        self.baud_suffix.setFixedWidth(10)
        self.baud_suffix.setPalette(QPalette(Qt.GlobalColor.transparent)) # set the label color to transparent
        self.parity_label = QLabel('Parity:')
        self.parity_combo = QComboBox()
        self.parity_suffix = QLabel('s')
        self.parity_suffix.setFixedWidth(10)
        self.parity_suffix.setPalette(QPalette(Qt.GlobalColor.transparent)) # set the label color to transparent
        self.interval_label = QLabel('Interval:')
        self.interval_spin = QSpinBox()
        self.interval_suffix = QLabel('s')
        self.interval_suffix.setFixedWidth(10)
        self.start_button = QPushButton('Start Reading')
        self.stop_button = QPushButton('Stop Reading')
        self.save_button = QPushButton('Save Data')
        self.text_edit = QTextEdit()

        # Add options to the combo boxes
        self.port_combo.addItems(self.get_serial_ports())
        self.baud_combo.addItems(['9600', '19200', '38400', '57600', '115200'])
        self.parity_combo.addItems(['S', 'N', 'E', 'O', 'M'])

        # Set default values for the combo boxes and spin box
        self.baud_combo.setCurrentText('9600')
        self.parity_combo.setCurrentText('S')
        self.interval_spin.setRange(1, 60)
        self.interval_spin.setValue(1)

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
        hbox5.addWidget(self.start_button)
        hbox5.addWidget(self.stop_button)
        hbox5.addWidget(self.save_button)
        vbox.addLayout(hbox1)
        vbox.addLayout(hbox2)
        vbox.addLayout(hbox3)
        vbox.addLayout(hbox4)
        vbox.addLayout(hbox5)
        vbox.addWidget(self.text_edit)

        # Set the layout for the window
        vbox.addStretch()
        self.setLayout(vbox)

        # Connect the signals to the slots
        self.start_button.clicked.connect(self.start_reading)
        self.stop_button.clicked.connect(self.stop_reading)
        self.save_button.clicked.connect(self.save_data)

        # Initialize the timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.read_data)

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

        # Initialize the serial connection
        self.ser = serial.Serial(port, baud, parity=parity, timeout=0)

        # Start the timer to read data at the specified interval
        self.timer.start(interval)

        # Disable start button and enable stop button
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_reading(self):
        # Stops reading data from the serial port
        self.timer.stop()
        self.ser.close()

        # Disable stop button and enable start button
        self.stop_button.setEnabled(False)
        self.start_button.setEnabled(True)

    def read_data(self):
        # Reads data from the serial port and displays it in the text edit box
        try:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            line = f'{timestamp}: {self.ser.readline().decode("utf-8").strip()}'
            self.text_edit.append(line)
        except serial.SerialException:
            timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            self.text_edit.append(f'{timestamp}: Error reading data from serial port')

    def save_data(self):
        # Saves the data in the text edit box to a file
        filename, _ = QFileDialog.getSaveFileName(self, 'Save Data', '', 'Text Files (*.txt)')
        if filename:
            with open(filename, 'w') as f:
                f.write(self.text_edit.toPlainText())

if __name__ == '__main__':
    app = QApplication(sys.argv)
    serial_reader = SerialReader()
    sys.exit(app.exec())