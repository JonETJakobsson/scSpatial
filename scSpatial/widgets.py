<<<<<<< HEAD
from configparser import MAX_INTERPOLATION_DEPTH
from email.charset import QP
from hashlib import sha1
from PyQt5.QtWidgets import QWidget, QLabel, QListWidget, QVBoxLayout, QHBoxLayout, QPushButton
=======
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
)
>>>>>>> 69deff2d2cca285abea2989143da2ef6733a76d3
from PyQt5.QtGui import QFont
from matplotlib.pyplot import show


h1 = QFont("Arial", 13)


class colorObjectWidget(QWidget):
    """Widget used to color objects by different features
    (currently gene expression)"""
    def __init__(self, dataset, viewer):
        super().__init__()
        self.dataset = dataset
        self.viewer = viewer
        self.initUI()

    def initUI(self):

        self.label = QLabel(self)
        self.label.setText("Color objects by gene:")
        self.label.setFont(h1)
        self.label.move(10, 10)

        # Gene selection list
        self.listwidget = QListWidget(self)
        self.listwidget.move(10, 10)

        for gene in self.dataset.segmentation[0].gene_expression.columns:
            self.listwidget.addItem(gene)

        self.listwidget.itemClicked.connect(self.color_genes)

        # Reset button
        self.reset_button = QPushButton(self)
        self.reset_button.setText("Reset")
        self.reset_button.clicked.connect(self.color_reset)

        # Layout of widget
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.label)
        vbox.addWidget(self.listwidget)
        vbox.addWidget(self.reset_button)
        # vbox.addStretch()
        hbox = QHBoxLayout(self)
        hbox.addLayout(vbox)
        hbox.addStretch()

        self.layout = hbox

    def color_genes(self, listItem):
        """Sets object color by selected gene"""
        import numpy as np
        from sklearn.preprocessing import minmax_scale
        from vispy.color.colormap import Colormap

        gene = listItem.text()
        values = self.dataset.segmentation[0].gene_expression[gene]
        values = np.log1p(values)
        values = minmax_scale(values)
        cmap = Colormap(["b", "r"])
        colors = cmap[values]
        self.viewer.layers["segmentation"].color = dict(
            zip(
                self.dataset.segmentation[0].gene_expression.index,
                colors.rgba
            )
        )
        # Change blending to additive to allow black objects to disapear
        self.viewer.layers["segmentation"].blending = "additive"

    def color_reset(self):
        """Reset object color to auto and translucent."""
        self.viewer.layers["segmentation"].color_mode = "auto"
        self.viewer.layers["segmentation"].blending = "translucent"


class kajsasWidget(QWidget):
    def __init__(self, dataset, viewer):
        super().__init__()
        self.dataset = dataset
        self.viewer = viewer
        self.initUI()

    def initUI(self):
<<<<<<< Updated upstream

        self.label = QLabel(self)
        self.label.setText("Choose files:")
        self.label.setFont(h1)

        # Tab 1.1
        self.tab1_1 = QWidget()
        self.tab1_1.layout = QVBoxLayout()
        self.btn_print = QPushButton('Please select a nucleai image')
=======
        pass
>>>>>>> Stashed changes
