from configparser import MAX_INTERPOLATION_DEPTH
from email.charset import QP
from hashlib import sha1
import sys
from PyQt5.QtWidgets import QWidget, QLabel, QListWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QLineEdit, QTabWidget, QGridLayout, QVBoxLayout
from PyQt5.QtGui import QFont
from matplotlib.pyplot import show

h1 = QFont("Arial", 13)

class kajsasWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
# self.dataset = dataset
# self.viewer = viewer
        self.initUI()

    def initUI(self):

        self.label = QLabel(self)
        self.label.setText("Select files:")
        self.label.setFont(h1)
        
        mainLayout = QGridLayout()
       

        # Tab 1
        self.tab1_1 = QWidget()
        self.tab1_1.layout = QVBoxLayout()

        self.btn_print = QPushButton('Please select a nuclei image')
        self.tab1_1.layout.addWidget(self.btn_print)

        self.tab1_1.setLayout(self.tab1_1.layout)


        self.tabs1 = QTabWidget()
        self.tabs1.addTab(self.tab1_1, 'Tab1')

        mainLayout.addWidget(self.tabs1, 0, 0)
        self.setLayout(mainLayout)


app = QApplication(sys.argv)

demo = kajsasWidget()
demo.show()

sys.exit(app.exec_())