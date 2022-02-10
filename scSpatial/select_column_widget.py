from configparser import MAX_INTERPOLATION_DEPTH
from email.charset import QP
from hashlib import sha1
import sys
from PyQt5.QtWidgets import QWidget, QLabel, QComboBox, QListWidget, QFormLayout, QVBoxLayout, QHBoxLayout, QPushButton, QApplication, QLineEdit, QTabWidget, QGridLayout, QSpinBox
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
            
        self.list_x = QComboBox()
        self.list_x.addItems(columns)
        self.list_y = QComboBox()
        self.list_y.addItems(columns)
        self.list_gene = QComboBox()
        self.list_gene.addItems(columns)

        layout = QFormLayout()
        layout.addRow("x", self.list_x)
        layout.addRow("y", self.list_y)
        layout.addRow("gene", self.list_gene)
        btn = QPushButton("Execute")
        btn.clicked.connect(self.print_selection)
        layout.addWidget(btn)

        self.setLayout(layout)

    def print_selection(self):
        print(self.list_x.currentText())

app = QApplication(sys.argv)

demo = selectColumnsWidget()
demo.show()

sys.exit(app.exec_())
