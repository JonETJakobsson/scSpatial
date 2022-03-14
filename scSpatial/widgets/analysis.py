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

from ..dataset import Dataset
from ..viewer import Viewer
from ..analysis import Bonefight

class analysisWidget(QWidget):
    """Widget used to run different analysis methods.
    BoneFight
    """

    def __init__(self, dataset: Dataset, viewer: Viewer):
        super().__init__()
        self.dataset = dataset
        self.viewer = viewer
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout(self)

        self.reference_btn = QPushButton("Select a reference dataset")
        self.reference_btn.clicked.connect(self.read_reference_dataset)

        self.groupby_combo = QComboBox(self)
        self.groupby_combo.currentTextChanged.connect(self.show_obs_example)

        self.obs_example_list = QListWidget(self)

        self.bonefight_btn = QPushButton("Run BoneFight analysis")
        self.bonefight_btn.clicked.connect(self.run_bonefight_analysis)
        self.bonefight_btn.setEnabled(False)

        self.layout.addWidget(self.reference_btn)
        self.layout.addWidget(QLabel("Select observation key:"))
        self.layout.addWidget(self.groupby_combo)
        self.layout.addWidget(self.obs_example_list)
        self.layout.addWidget(QLabel("BoneFight analysis"))
        self.layout.addWidget(self.bonefight_btn)
        self.layout.addStretch()
        self.setLayout(self.layout)

    def read_reference_dataset(self):
        import scanpy as sc

        path = QFileDialog.getOpenFileName(self, caption="Select reference dataset")[0]

        self.reference_adata = sc.read(path)

        if len(self.reference_adata.obs_keys()) > 0:
            self.groupby_combo.addItems(self.reference_adata.obs_keys())
        else:
            print("Error: reference dataset must contain atleast one observation")

    def show_obs_example(self, key: str):
        from random import sample

        self.obs_example_list.clear()
        example_list = sample(list(set(self.reference_adata.obs[key])), k=10)
        self.obs_example_list.addItems([str(example) for example in example_list])
        self.bonefight_btn.setEnabled(True)

    def run_bonefight_analysis(self):
        # Instantiate the bonefight object
        bf_model = Bonefight(
            segmentation=self.dataset.active_segmentation,
            reference=self.reference_adata,
            groupby=self.groupby_combo.currentText(),
        )

        cell_types = bf_model.transfer_labels()
        self.dataset.active_segmentation.add_cell_types(cell_types)
