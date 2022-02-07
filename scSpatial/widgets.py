from PyQt5.QtWidgets import QWidget, QLabel, QListWidget, QVBoxLayout, QHBoxLayout
from PyQt5.QtGui import QFont


h1 = QFont("Arial", 13)


class colorObjectWidget(QWidget):
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

        self.listwidget = QListWidget(self)
        self.listwidget.move(10, 10)

        for gene in self.dataset.segmentation[0].gene_expression.columns:
            self.listwidget.addItem(gene)

        # Connect selection to action
        self.listwidget.itemClicked.connect(self.geneIsSelected)

        # Cosmetic layout of widget
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.label)
        vbox.addWidget(self.listwidget)
        # vbox.addStretch()
        hbox = QHBoxLayout(self)
        hbox.addLayout(vbox)
        hbox.addStretch()

        self.layout = hbox

    def geneIsSelected(self, listItem):
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
            zip(self.dataset.segmentation[0].gene_expression.index, colors.rgba)
        )


class kajsasWidget(QWidget):
    def __init__(self, dataset, viewer):
        super().__init__()
        self.dataset = dataset
        self.viewer = viewer
        self.initUI()

    def initUI(self):
