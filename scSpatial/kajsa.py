
from configparser import MAX_INTERPOLATION_DEPTH
from email.charset import QP
from hashlib import sha1
from os import getcwd
import os
import sys
import this
from tkinter import dialog
from urllib import response
from PyQt5.QtWidgets import QWidget, QLabel, QListWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QLineEdit, QTabWidget, QGridLayout, QVBoxLayout, QFileDialog, QComboBox, QFormLayout
from PyQt5.QtGui import QFont
from click import option
from matplotlib.pyplot import show

h1 = QFont("Arial", 13)

class kajsasWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(500, 200)
        self.initUI()

    def initUI(self):
        
        layout = QFormLayout()
        self.setLayout(layout)

        btn_nuclei = QPushButton('Select a nuclei image')
        btn_nuclei.clicked.connect(self.launchNucleiDialog)
        layout.addWidget(btn_nuclei)

        btn_cytoplasm = QPushButton('Select a cytoplasm image')
        btn_cytoplasm.clicked.connect(self.launchCytoplasmDialog)
        layout.addWidget(btn_cytoplasm)

        btn_other = QPushButton('Other channel')
        btn_other.clicked.connect(self.launchOtherDialog)
        layout.addWidget(btn_other)

        self.label = QLabel(self)

    def launchNucleiDialog(self):
        
        fname = QFileDialog.getOpenFileName(self, 'Select a nuclei image', '')

        if fname:
            self.label.setText(fname[0])

    def launchCytoplasmDialog(self):
        
        fname = QFileDialog.getOpenFileName(self, 'Select a cytoplasm image', '')

        if fname:
            self.label.setText(fname[0])

    def launchOtherDialog(self):
        
        fname = QFileDialog.getOpenFileName(self, 'Select other channel', '')

        if fname:
            self.label.setText(fname[0])
    

app = QApplication(sys.argv)

demo = kajsasWidget()
demo.show()

sys.exit(app.exec_())
