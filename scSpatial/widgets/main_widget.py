from PyQt5.QtWidgets import QWidget, QTabWidget, QApplication, QVBoxLayout
from PyQt5.QtGui import QFont
from napari import Viewer

import sys

from .loaddata import loadWidget
from .segmentation import segmentationWidget
from .analysis import analysisWidget
from .visualization import visualizationWidget
from ..dataset import Dataset



# Main widget presents the tabs and can provide other global tools
class mainWidget(QWidget):
    def __init__(self, dataset: Dataset, viewer: Viewer):
        super().__init__()
        self.dataset = dataset
        self.viewer = viewer
        self.initUI()

    def initUI(self):

        # Widgets will be added vertically
        layout = QVBoxLayout(self)

        # Create tabs with names to access induvidual widgets
        self.tabs = QTabWidget()
        self.tabs.addTab(loadWidget(self.dataset, self.viewer), "Load Data")
        self.tabs.addTab(segmentationWidget(self.dataset, self.viewer), "Segmentation")
        self.tabs.addTab(analysisWidget(self.dataset, self.viewer), "Analysis")
        self.tabs.addTab(visualizationWidget(self.dataset, self.viewer), "Visualization")

        # Add all widgets in order
        layout.addWidget(self.tabs)

        # Set layout on mainWidget
        self.setLayout(layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    demo = mainWidget("dataset", "viewer")
    demo.show()

    sys.exit(app.exec_())
