
from configparser import MAX_INTERPOLATION_DEPTH
from email.charset import QP
from hashlib import sha1
from os import getcwd
import os
import sys
import this
from tkinter import dialog
from urllib import response
from PyQt5.QtWidgets import QWidget, QLabel, QListWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QLineEdit, QTabWidget, QGridLayout, QVBoxLayout, QFileDialog, QComboBox, QFormLayout, QDialogButtonBox
from PyQt5.QtGui import QFont
from click import option
from matplotlib.pyplot import show
from torch import layout

h1 = QFont("Arial", 13)

class kajsasWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(500, 200)
        self.initUI()

    def initUI(self):
        
        layout = QGridLayout()
        
        btn_nuclei = QPushButton('Select a nuclei image')
        btn_nuclei.clicked.connect(self.launchNucleiDialog)
        layout.addWidget(btn_nuclei, 0, 0)

        btn_cytoplasm = QPushButton('Select a cytoplasm image')
        btn_cytoplasm.clicked.connect(self.launchCytoplasmDialog)
        layout.addWidget(btn_cytoplasm, 1, 0)

        btn_other = QPushButton('Other channel')
        btn_other.clicked.connect(self.launchOtherDialog)
        layout.addWidget(btn_other, 2, 0)
        
        self.label_nuc = QLabel("")
        layout.addWidget(self.label_nuc, 0, 1)

        self.label_cyto = QLabel("")
        layout.addWidget(self.label_cyto, 1, 1)

        self.label_other = QLabel("")
        layout.addWidget(self.label_other, 2, 1)

        self.setLayout(layout)

    def launchNucleiDialog(self):
        
        file = QFileDialog.getOpenFileName(self, 'Select a nuclei image', '')[0]
        fname = file.split("/")[-1]

        if file:
            self.label_nuc.setText(fname)

    def launchCytoplasmDialog(self):
        
        file = QFileDialog.getOpenFileName(self, 'Select a cytoplasm image', '')[0]
        fname = file.split("/")[-1]

        if file:
            self.label_cyto.setText(fname)

    def launchOtherDialog(self):
        
        file = QFileDialog.getOpenFileName(self, 'Select other channel', '')[0]
        fname = file.split("/")[-1]

        if file:
            self.label_other.setText(fname)
    

app = QApplication(sys.argv)

demo = kajsasWidget()
demo.show()

sys.exit(app.exec_())
