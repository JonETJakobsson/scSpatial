from configparser import MAX_INTERPOLATION_DEPTH
from email.charset import QP
from hashlib import sha1
import sys
from PyQt5.QtWidgets import QWidget, QLabel, QListWidget, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QLineEdit, QTabWidget, QGridLayout, QVBoxLayout
from PyQt5.QtGui import QFont
from matplotlib.pyplot import show

h1 = QFont("Arial", 13)

class selectColumnsWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(800, 600)
# self.dataset = dataset
# self.viewer = viewer
        self.initUI()

    def initUI(self):
        columns = ["x", "y", "other", "gene"]
        label_x = QLabel("x")
        label_y = QLabel("y")
        label_gene = QLabel("gene")
        list_x = QListWidget()
        list_x.addItems(columns)
        list_y = QListWidget()
        list_y.addItems(columns)
        list_gene = QListWidget()
        list_gene.addItems(columns)

        label_layout = QHBoxLayout()
        label_layout.addWidget(label_x)
        label_layout.addWidget(label_y)
        label_layout.addWidget(label_gene)

        list_layout = QHBoxLayout()
        list_layout.addWidget(list_x)
        list_layout.addWidget(list_y)
        list_layout.addWidget(list_gene)

        layout = QVBoxLayout()
        layout.addLayout(label_layout)
        layout.addLayout(list_layout)

        self.setLayout(layout)
app = QApplication(sys.argv)

demo = selectColumnsWidget()
demo.show()

sys.exit(app.exec_())
