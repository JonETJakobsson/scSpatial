import plotly.express as px
import pandas as pd
import imageio
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import (
    QApplication,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
    QTableWidget,
    QTableWidgetItem)
from PyQt5.QtWebEngineWidgets import QWebEngineView

import sys

from ..dataset import Dataset, Segmentation, segmentCytoplasm, segmentNuclei
from ..viewer import Viewer
from ..analysis import Bonefight

h1 = QFont("Arial", 13)


class loadWidget(QWidget):
    """Widget holding all widgets used for loading data"""

    def __init__(self, dataset: Dataset, viewer: Viewer):
        super().__init__()
        self.dataset = dataset
        self.viewer = viewer
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.addWidget(loadImageWidget(self.dataset, self.viewer))
        layout.addWidget(loadGenesWidget(self.dataset, self.viewer))
        self.setLayout(layout)


class loadImageWidget(QWidget):
    """Widget used for loading images"""

    def __init__(self, dataset: Dataset, viewer: Viewer):
        super().__init__()
        self.dataset = dataset
        self.viewer = viewer
        self.nuclei_path = None
        self.cytoplasm_path = None
        self.other_path = None
        self.initUI()

    def initUI(self):

        layout = QGridLayout()
        layout.setColumnMinimumWidth(1, 100)

        btn_nuclei = QPushButton("Nuclei")
        btn_nuclei.clicked.connect(self.launchNucleiDialog)
        btn_nuclei.setToolTip("Select a nuclei imagee")
        layout.addWidget(btn_nuclei, 0, 0)

        btn_cytoplasm = QPushButton("Cytoplasm")
        btn_cytoplasm.clicked.connect(self.launchCytoplasmDialog)
        btn_cytoplasm.setToolTip("Select a cytoplasm image")
        layout.addWidget(btn_cytoplasm, 1, 0)

        btn_other = QPushButton("Other")
        btn_other.clicked.connect(self.launchOtherDialog)
        btn_other.setToolTip("Other channel")
        layout.addWidget(btn_other, 2, 0, alignment=Qt.AlignTop)

        self.label_nuc = QLabel("")
        layout.addWidget(self.label_nuc, 0, 1)

        self.label_cyto = QLabel("")
        layout.addWidget(self.label_cyto, 1, 1)

        self.label_other = QLabel("")
        layout.addWidget(self.label_other, 2, 1, alignment=Qt.AlignTop)

        self.setLayout(layout)

    def launchNucleiDialog(self):
        path = QFileDialog.getOpenFileName(self, "Select a nuclei image", "")[0]
        self.nuclei_path = path
        file_name = path.split("/")[-1]

        if path:
            self.label_nuc.setText(file_name)
            self.dataset.load_nuclei(self.nuclei_path)
            self.viewer.add_nuclei(self.dataset)

    def launchCytoplasmDialog(self):
        path = QFileDialog.getOpenFileName(self, "Select a cytoplasm image", "")[0]
        self.cytoplasm_path = path
        file_name = path.split("/")[-1]

        if path:
            self.label_cyto.setText(file_name)
            self.dataset.load_cytoplasm(self.cytoplasm_path)
            self.viewer.add_cytoplasm(self.dataset)

    def launchOtherDialog(self):
        # TODO Add ability to name added channel
        path = QFileDialog.getOpenFileName(self, "Select other channel", "")[0]
        self.other_path = path
        fname = path.split("/")[-1]

        if path:
            self.label_other.setText(fname)
            self.dataset.load_other_channel(channel="other", path=self.other_path)
            self.viewer.add_other_channel(self.dataset, channel="other")

class loadGenesWidget(QWidget):
    """Widget used for loading gene expression file"""

    def __init__(self, dataset: Dataset, viewer: Viewer):
        super().__init__()
        self.dataset = dataset
        self.viewer = viewer
        self.initUI()

    def initUI(self):
        # Button to open file dialog
        self.btn_load_file = QPushButton("Select gene file")
        self.btn_load_file.setToolTip("Open a csv file")
        self.btn_load_file.clicked.connect(self.load_df)

        # Use form layout and add button to the top
        self.layout = QFormLayout()
        self.layout.addWidget(self.btn_load_file)

        # Set the layout to the loadGenesWidget
        self.setLayout(self.layout)

    def load_df(self):
        """Runns the file dialog and add more elements to the
        UI for selecting correct columns"""

        import pandas as pd

        # Fetch path to file, note that this return a
        # tuple and path is on index 0
        path = QFileDialog.getOpenFileName(
            self, caption="select a gene expression file"
        )

        # read in the gene expression file into df
        # and also store columns in a variable
        self.df = pd.read_csv(path[0])
        self.columns = self.df.columns

        # Create the selection widgets and add the columns options
        self.list_x = QComboBox()
        self.list_y = QComboBox()
        self.list_gene = QComboBox()
        self.list_x.addItems(self.columns)
        self.list_y.addItems(self.columns)
        self.list_gene.addItems(self.columns)

        # If we recognize the columns, preset the values
        if "PosX" and "PosY" and "Gene" in self.columns:
            self.list_x.setCurrentText("PosX")
            self.list_y.setCurrentText("PosY")
            self.list_gene.setCurrentText("Gene")

        # Add the widgets to the form layout
        self.layout.addRow("x", self.list_x)
        self.layout.addRow("y", self.list_y)
        self.layout.addRow("gene", self.list_gene)

        # Add a confirmation button to the bottom of the UI
        self.btn_confirm_columns = QPushButton("Confirm")
        self.btn_confirm_columns.clicked.connect(self.save_df_to_dataset)
        self.layout.addWidget(self.btn_confirm_columns)

    def save_df_to_dataset(self):
        """Renames the columns of the gene expression dataframe
        and stores it in the dataset. Furthermore adds these to the viewer"""
        # Find file representation of columns
        x = self.list_x.currentText()
        y = self.list_y.currentText()
        gene = self.list_gene.currentText()

        # Filter on x y and gene
        self.df = self.df[[x, y, gene]]
        # Rename columns to standardized names
        self.df.columns = ["x", "y", "gene"]

        # Set gene column as category
        self.df.gene = self.df.gene.astype("category")

        # Save gene expression to the dataset
        self.dataset.add_gene_expression(self.df)

        self.btn_confirm_columns.setVisible(False)

        # Load gene into the viewer
        self.viewer.add_genes(self.dataset)
        
if __name__ == "__main__":
    app = QApplication(sys.argv)

    demo = loadImageWidget("dataset", "viewer")
    demo.show()

    sys.exit(app.exec_())
