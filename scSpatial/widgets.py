from re import X
from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QListWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QComboBox,
    QFormLayout,
    QApplication,
    QFileDialog,
    QGridLayout
)
from PyQt5.QtGui import QFont
import sys

from pydantic import NoneBytes, NoneIsAllowedError
from dataset import Dataset
from napari import Viewer


h1 = QFont("Arial", 13)

class loadWidget(QWidget):
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
    def __init__(self, dataset: Dataset, viewer: Viewer):
        super().__init__()
        self.dataset = dataset
        self.viewer = viewer
        self.nuclei_path = None
        self.cytoplasm_path = None
        self.other_path = None
        self.initUI()

    def initUI(self):
        
        layout = QGridLayout(self)
        layout.setColumnMinimumWidth(1, 100)
        
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

        self.btn_load = QPushButton("Load images")
        self.btn_load.clicked.connect(self.load_images)
        layout.addWidget(self.btn_load, 3, 0, 1, 2)

        self.setLayout(layout)

    def launchNucleiDialog(self):
        
        path = QFileDialog.getOpenFileName(self, 'Select a nuclei image', '')[0]
        self.nuclei_path = path
        fname = path.split("/")[-1]

        if path:
            self.label_nuc.setText(fname)

    def launchCytoplasmDialog(self):
        
        path = QFileDialog.getOpenFileName(self, 'Select a cytoplasm image', '')[0]
        self.cytoplasm_path = path
        fname = path.split("/")[-1]

        if path:
            self.label_cyto.setText(fname)

    def launchOtherDialog(self):
        
        path = QFileDialog.getOpenFileName(self, 'Select other channel', '')[0]
        self.other_path = path
        fname = path.split("/")[-1]

        if path:
            self.label_other.setText(fname)

    def load_images(self):
        self.btn_load.setVisible(False)
        if self.nuclei_path:
            self.dataset.load_nuclei(self.nuclei_path)
            self.viewer.add_image(self.dataset.images["Nuclei"], name="Nuclei", colormap="yellow")
        
        if self.cytoplasm_path:
            self.dataset.load_cytoplasm(self.cytoplasm_path)
            self.viewer.add_image(self.dataset.images["Cytoplasm"], name="Cytoplasm", colormap="cyan")
        
        if self.other_path:
            self.dataset.load_other_channel(path=self.other_path)
            self.viewer.add_image(self.dataset.images["Other"], name="Other", colormap="magenta")

class loadGenesWidget(QWidget):
    def __init__(self, dataset: Dataset, viewer: Viewer):
        super().__init__()
        self.dataset = dataset
        self.viewer = viewer
        self.initUI()

    def initUI(self):
        # Button to open file dialog
        self.btn_load_file = QPushButton("Select gene file")
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
            self,
            caption="select a gene expression file"
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
        if "PosX" in self.columns and "PosY" in self.columns and "Gene" in self.columns:
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
        #Find file representation of columns
        x = self.list_x.currentText()
        y = self.list_y.currentText()
        gene = self.list_gene.currentText()

        # Filter on x y and gene
        self.df = self.df[[x, y, gene]]
        # Rename columns to standardized names
        self.df.columns = ["x", "y", "gene"]

        #Set gene column as category
        self.df.gene = self.df.gene.astype("category")

        # Save gene expression to the dataset
        self.dataset.gene_expression = self.df

        self.btn_confirm_columns.setVisible(False)

        # Load gene into the viewer
        # TODO I would like to see all functions adding data to the viewer 
        # somewhere else (together), as it makes it easier to change the apearance of the app
        # Now we have to look through random widgets to change these things.
        from vispy.color.colormap import get_colormap

        cm = get_colormap("gist_rainbow")
        codes = self.dataset.gene_expression.gene.cat.codes
        colors = cm.map(codes/max(codes))
        # color_map = dict(zip(self.dataset.gene_expression.gene.cat.categories, normalized_codes))
        # colors = list(self.dataset.gene_expression.gene.map(color_map))
        text_property = {
            "text": "{gene}",
            "size": 12,
            "color": "white",
            "translation": (-3,0),
            "visible": False
        }
        self.viewer.add_points(
            data=list(zip(
                self.dataset.gene_expression.y,
                self.dataset.gene_expression.x
            )),
            properties=self.dataset.gene_expression,
            name="Genes",
            text=text_property,
            face_color=colors
        )
        
class segmentationWidget(QWidget):
    def __init__(self, dataset: Dataset, viewer: Viewer):
        super().__init__()
        self.dataset = dataset
        self.viewer = viewer
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout(self)
        self.selection_layout = QVBoxLayout(self)
        self.option_layout = QFormLayout(self)

        method_label = QLabel("Segmentation method")
        self.selection_layout.addWidget(method_label)

        self.method_combo = QComboBox(self)
        self.method_combo.addItems([
            "select method",
            "Cellpose - Nuclei",
            "Cellpose - Cytoplasm",
            "External"
            ]
        )
        self.method_combo.currentTextChanged.connect(self.create_option_widget)

        self.selection_layout.addWidget(self.method_combo)

        self.main_layout.addLayout(self.selection_layout)
        self.main_layout.addLayout(self.option_layout)
        self.setLayout(self.main_layout)

    def create_option_widget(self):
        print(self.method_combo.currentText())

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


if __name__ == "__main__":
    app = QApplication(sys.argv)

    demo = loadImageWidget("dataset", "viewer")
    demo.show()

    sys.exit(app.exec_())
