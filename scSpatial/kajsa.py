from configparser import MAX_INTERPOLATION_DEPTH
from email.charset import QP
from hashlib import sha1
from os import getcwd
import os
import sys
import this
from tkinter import dialog
from urllib import response
from PyQt5.QtWidgets import QWidget, QLabel, QListWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QLineEdit, QTabWidget, QGridLayout, QVBoxLayout, QFileDialog, QComboBox
from PyQt5.QtGui import QFont
from click import option
from matplotlib.pyplot import show

h1 = QFont("Arial", 13)

class kajsasWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(500, 200)
# self.dataset = dataset
# self.viewer = viewer
        self.initUI()

    def initUI(self):

        self.label = QLabel(self)
        self.label.setText("Select file from drop down menu:") #Kan jag fixa så detta får plats?
        self.label.setFont(h1)
        
        mainLayout = QGridLayout()
       
        # Test file dialog
        layout = QVBoxLayout()
        self.setLayout(layout)

        self.options = ('Select a nuclei image', 'Select a cytoplasm image', 'Select a gene expression file')

        self.combo = QComboBox()
        self.combo.addItems(self.options)
        layout.addWidget(self.combo)

        btn = QPushButton('Load')
        btn.clicked.connect(self.launchDialog)
        layout.addWidget(btn)

    def launchDialog(self):
        option = self.options.index(self.combo.currentText())

        if option == 0:
            response = self.SelectaNucleiImage()
        elif option == 1:
            response = self.SelectaCytoplasmImage()
        elif option == 2:
            option = self.SelectaGeneExpressionFile()
        else:
            print('Got nothing')
    
    def SelectaNucleiImage(self):

        response = QFileDialog.getOpenFileName(
            parent=self,
            caption='Please select a nuclei image',
            directory=os.getcwd()
            #Jag kan lägga till filter på vad för sorts filer som kan användas
        
        )

        print(response)
        return response [0]

app = QApplication(sys.argv)

demo = kajsasWidget()
demo.show()

sys.exit(app.exec_())
