from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QFormLayout,
)
from PyQt5.QtGui import QFont


h1 = QFont("Arial", 13)


class geneColumnSelectWidget(QWidget):
    def __init__(self, dataset, viewer):
        super().__init__()
        self.dataset = dataset
        self.viewer = viewer
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
