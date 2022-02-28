
import sys
from unicodedata import name


import imageio
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtWidgets import (QApplication, QComboBox, QFileDialog, QFormLayout,
                             QGridLayout, QHBoxLayout, QLabel, QListWidget,
                             QPushButton, QSlider, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem)
from numpy import array_str

from dataset import Dataset, Segmentation, segmentCytoplasm, segmentNuclei
from viewer import Viewer
from analysis import Bonefight

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

        btn_nuclei = QPushButton("Select a nuclei image")
        btn_nuclei.clicked.connect(self.launchNucleiDialog)
        layout.addWidget(btn_nuclei, 0, 0)

        btn_cytoplasm = QPushButton("Select a cytoplasm image")
        btn_cytoplasm.clicked.connect(self.launchCytoplasmDialog)
        layout.addWidget(btn_cytoplasm, 1, 0)

        btn_other = QPushButton("Other channel")
        btn_other.clicked.connect(self.launchOtherDialog)
        layout.addWidget(btn_other, 2, 0, alignment = Qt.AlignTop)

        self.label_nuc = QLabel("")
        layout.addWidget(self.label_nuc, 0, 1)

        self.label_cyto = QLabel("")
        layout.addWidget(self.label_cyto, 1, 1)

        self.label_other = QLabel("")
        layout.addWidget(self.label_other, 2, 1, alignment = Qt.AlignTop)

        self.setLayout(layout)

    def launchNucleiDialog(self):
        path = QFileDialog.getOpenFileName(
            self,
            "Select a nuclei image",
            ""
        )[0]
        self.nuclei_path = path
        file_name = path.split("/")[-1]

        if path:
            self.label_nuc.setText(file_name)
            self.dataset.load_nuclei(self.nuclei_path)
            self.viewer.add_nuclei(self.dataset)

    def launchCytoplasmDialog(self):
        path = QFileDialog.getOpenFileName(
            self,
            "Select a cytoplasm image",
            ""
        )[0]
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
            self.dataset.load_other_channel(
                channel="other",
                path=self.other_path
            )
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
        self.dataset.gene_expression = self.df

        self.btn_confirm_columns.setVisible(False)

        # Load gene into the viewer
        self.viewer.add_genes(self.dataset)


class segmentationWidget(QWidget):
    """Collection of all widgets used under the segmentation tab"""
    def __init__(self, dataset: Dataset, viewer: Viewer):
        super().__init__()
        self.dataset = dataset
        self.viewer = viewer
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        layout.addWidget(segmentationCreateWidget(self.dataset, self.viewer))
        layout.addWidget(segmentationControlWidget(self.dataset, self.viewer))
        self.setLayout(layout)


class segmentationCreateWidget(QWidget):
    """Widget used to run segmentation of the dataset"""

    def __init__(self, dataset: Dataset, viewer: Viewer):
        super().__init__()
        self.dataset = dataset
        self.viewer = viewer
        self.initUI()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.selection_layout = QVBoxLayout()
        self.option_layout = QFormLayout()

        method_label = QLabel("Segmentation method")
        self.selection_layout.addWidget(method_label)

        self.method_combo = QComboBox()
        self.method_combo.addItems(
            [
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
        # Clear option_layout if rows exists
        if self.option_layout.rowCount() > 0:
            for _ in range(self.option_layout.rowCount()):
                self.option_layout.removeRow(0)

        option = self.method_combo.currentText()
        if option == "Cellpose - Nuclei" or option == "Cellpose - Cytoplasm":
            h1_layout = QHBoxLayout()
            self.sldr_size = QSlider(Qt.Horizontal)
            self.sldr_size.setRange(0, 200)
            if option == "Cellpose - Nuclei":
                self.sldr_size.setValue(70)
            else:
                self.sldr_size.setValue(120)
            self.sldr_size.valueChanged.connect(self.value_change)
            self.lbl_size = QLabel("")
            self.lbl_size.setText(str(self.sldr_size.value()))
            h1_layout.addWidget(self.sldr_size)
            h1_layout.addWidget(self.lbl_size)
            self.option_layout.addRow("Size of nuclei", h1_layout)

            h2_layout = QHBoxLayout()
            self.sldr_flow_th = QSlider(Qt.Horizontal)
            self.sldr_flow_th.setRange(0, 100)
            self.sldr_flow_th.setValue(40)
            self.sldr_flow_th.valueChanged.connect(self.value_change)
            self.lbl_flow_th = QLabel("")
            self.lbl_flow_th.setText(str(self.sldr_flow_th.value() / 100))
            h2_layout.addWidget(self.sldr_flow_th)
            h2_layout.addWidget(self.lbl_flow_th)
            self.option_layout.addRow("Flow threshold", h2_layout)

            h3_layout = QHBoxLayout()
            self.sldr_mask_th = QSlider(Qt.Horizontal)
            self.sldr_mask_th.setRange(0, 120)
            self.sldr_mask_th.setValue(60)
            self.sldr_mask_th.valueChanged.connect(self.value_change)
            self.lbl_mask_th = QLabel("")
            self.lbl_mask_th.setText(
                str((self.sldr_mask_th.value() - 60) / 10)
            )
            h3_layout.addWidget(self.sldr_mask_th)
            h3_layout.addWidget(self.lbl_mask_th)
            self.option_layout.addRow("Mask threshold", h3_layout)

            btn_run_test = QPushButton("Test run")
            btn_run_test.clicked.connect(self.run_segmentation_test)

            btn_run = QPushButton("Run")
            btn_run.clicked.connect(self.run_segmentation)

            self.option_layout.addWidget(btn_run_test)
            self.option_layout.addWidget(btn_run)

        if option == "External":
            btn_load_segmentation = QPushButton("Load segmentation file")
            btn_load_segmentation.clicked.connect(self.load_segmentation_file)
            self.option_layout.addWidget(btn_load_segmentation)

    def value_change(self, value):
        if self.sender() == self.sldr_size:
            self.lbl_size.setText(str(value))

        elif self.sender() == self.sldr_flow_th:
            self.lbl_flow_th.setText(str(value / 100))

        elif self.sender() == self.sldr_mask_th:
            value = (value - 60) / 10
            self.lbl_mask_th.setText(str(value))

    def load_segmentation_file(self):
        path = QFileDialog.getOpenFileName(
            self,
            caption="select a segmentation file"
        )[0]

        masks = imageio.imread(path).astype(int)
        seg = Segmentation(dataset=self.dataset, type="External")
        seg.objects = masks
        seg.map_genes()

        self.dataset.add_segmentation(seg)
        self.viewer.add_segmentation(seg, self.dataset)

    def run_segmentation_test(self):
        _, y, x = self.viewer.camera.center
        crop = self.dataset.crop(center=(y, x))

        size = int(self.lbl_size.text())
        f_th = float(self.lbl_flow_th.text())
        m_th = float(self.lbl_mask_th.text())

        if self.method_combo.currentText() == "Cellpose - Nuclei":
            seg = segmentNuclei(
                dataset=crop,
                size=size,
                flow_threshold=f_th,
                mask_threshold=m_th
            )
        if self.method_combo.currentText() == "Cellpose - Cytoplasm":
            seg = segmentCytoplasm(
                dataset=crop,
                size=size,
                flow_threshold=f_th,
                mask_threshold=m_th
            )

        seg.run()
        seg.map_genes()
        self.viewer.add_segmentation(seg, crop)
        # Manually add segmentation to dataset as it will
        # only be added to the Crop dataset otherwise
        self.dataset.add_segmentation(seg)

    def run_segmentation(self):
        size = int(self.lbl_size.text())
        f_th = float(self.lbl_flow_th.text())
        m_th = float(self.lbl_mask_th.text())

        if self.method_combo.currentText() == "Cellpose - Nuclei":
            seg = segmentNuclei(
                dataset=self.dataset,
                size=size,
                flow_threshold=f_th,
                mask_threshold=m_th
            )
        if self.method_combo.currentText() == "Cellpose - Cytoplasm":
            seg = segmentCytoplasm(
                dataset=self.dataset,
                size=size,
                flow_threshold=f_th,
                mask_threshold=m_th
            )

        seg.run()
        seg.map_genes()

        self.viewer.add_segmentation(seg, self.dataset)


class segmentationControlWidget(QWidget):
    """Widget used to run segmentation of the dataset"""

    def __init__(self, dataset: Dataset, viewer: Viewer):
        super().__init__()
        self.dataset = dataset
        self.viewer = viewer
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()
        self.lbl = QLabel("Segmentation list:")
        self.layout.addWidget(self.lbl)

        self.dataset.com.segmentation_list_changed.connect(
            self.update_segmentation_list
        )

        self.seg_table = QTableWidget(self)
        self.layout.addWidget(self.seg_table)

        remove_btn = QPushButton("Delete segmentation")
        remove_btn.clicked.connect(self.remove_row)
        self.layout.addWidget(remove_btn)

        add_btn = QPushButton("Add to viewer")
        add_btn.clicked.connect(self.add_to_viewer)
        self.layout.addWidget(add_btn)

        set_btn = QPushButton("Set as active segmentation")
        set_btn.clicked.connect(self.set_active)
        self.layout.addWidget(set_btn)

        self.layout.addStretch()
        self.setLayout(self.layout)

    def remove_row(self):
        row = self.seg_table.currentRow()
        id = self.seg_table.item(row, 0)
        self.viewer.remove_segmentation(seg=self.dataset.segmentation[int(id.text())])
        self.dataset.remove_segmentation(seg=self.dataset.segmentation[int(id.text())])

    def add_to_viewer(self):
        #TODO check if segmentation already is in list
        row = self.seg_table.currentRow()
        id = self.seg_table.item(row, 0)
        self.viewer.add_segmentation(seg=self.dataset.segmentation[int(id.text())], dataset=self.dataset)

    def set_active(self):
        row = self.seg_table.currentRow()
        id = self.seg_table.item(row, 0)
        self.dataset.set_active_segmentation(self.dataset.segmentation[int(id.text())])
        self.update_segmentation_list()
        for column in range(3):
            item = self.seg_table.item(row, column)
            item.setBackground(QColor(255, 128, 128))


    def update_segmentation_list(self):
        self.seg_table.clear()
        self.seg_table.setColumnCount(3)
    
        self.seg_table.setHorizontalHeaderLabels(["ID", "Type", "Settings"])
        
        if len(self.dataset.segmentation) > 0:
            print("adding")
            self.seg_table.setRowCount(len(self.dataset.segmentation))
            i = 0
            for _, seg in self.dataset.segmentation.items():
                id = QTableWidgetItem(str(seg.id))
                seg_type = QTableWidgetItem(seg.type)
                settings = QTableWidgetItem(str(seg.settings))
                self.seg_table.setItem(i, 0, id)
                self.seg_table.setItem(i, 1, seg_type)
                self.seg_table.setItem(i, 2, settings)
                i = i + 1
        
        self.seg_table.resizeColumnsToContents()
    
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
        path = QFileDialog.getOpenFileName(
            self, 
            caption="Select reference dataset"
        )[0]

        self.reference_adata = sc.read(path)

        if len(self.reference_adata.obs_keys()) > 0:
            self.groupby_combo.addItems(
                self.reference_adata.obs_keys()
            )
        else:
            print("Error: reference dataset must contain atleast one observation")

    def show_obs_example(self, key: str):
        from random import sample
        self.obs_example_list.clear()
        example_list = sample(list(set(self.reference_adata.obs[key])), k=10)
        self.obs_example_list.addItems(
            [str(example) for example in example_list]
        )
        self.bonefight_btn.setEnabled(True)

    def run_bonefight_analysis(self):
        # Instantiate the bonefight object
        bf_model = Bonefight(
            segmentation=self.dataset.active_segmentation,
            reference=self.reference_adata,
            groupby=self.groupby_combo.currentText()
        )

        cell_types = bf_model.transfer_labels()
        self.dataset.active_segmentation.add_cell_types = cell_types


class colorObjectWidget(QWidget):
    """Widget used to color objects by different features
    (currently gene expression)"""

    def __init__(self, dataset: Dataset, viewer: Viewer):
        super().__init__()
        self.dataset = dataset
        self.viewer = viewer
        self.initUI()

    def initUI(self):

        self.label = QLabel(self)
        self.label.setText("Select segmentation")
        self.label.setFont(h1)

        # Segmentation selection list
        self.seg_combo = QComboBox(self)
        self.dataset.com.segmentation_list_changed.connect(self.populate_seg_combo)

        # Set when to update visualization options
        self.seg_combo.currentTextChanged.connect(self.populate_options)
        self.dataset.com.active_segmentation_changed.connect(self.populate_options)
        self.dataset.com.cell_types_changed.connect(self.populate_options)

        # Gene selection list
        self.gene_combo = QComboBox(self)
        # When gene is selected
        self.gene_combo.currentTextChanged.connect(self.color_genes)

        # Cell type selection list
        self.cell_type_combo = QComboBox(self)
        # When cell type is selected
        self.cell_type_combo.currentTextChanged.connect(self.color_cell_type)

        # Reset button
        self.reset_button = QPushButton(self)
        self.reset_button.setText("Reset")
        self.reset_button.clicked.connect(self.color_reset)

        # Layout of widget
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.label)
        vbox.addWidget(self.seg_combo)
        vbox.addWidget(QLabel("Color by gene:"))
        vbox.addWidget(self.gene_combo)
        vbox.addWidget(QLabel("Color by cell type:"))
        vbox.addWidget(self.cell_type_combo)
        vbox.addWidget(self.reset_button)
        vbox.addStretch()

        self.layout = vbox

    def populate_seg_combo(self):
        self.seg_combo.clear()
        if len(self.dataset.segmentation) > 0:
            for _, seg in self.dataset.segmentation.items():
                self.seg_combo.addItem(str(seg.id))
    
    def populate_options(self):
        """draws visualization options based on the available data in segmentation"""
        import pandas as pd

        self.seg = self.dataset.active_segmentation
       
        used_genes = []
        for gene in self.seg.gene_expression.columns:
            if sum(self.seg.gene_expression[gene]) > 0:
                used_genes.append(gene)

        self.seg.gene_expression = self.seg.gene_expression[used_genes]

        self.gene_combo.clear()
        for gene in self.seg.gene_expression.columns:
            self.gene_combo.addItem(gene)

        # If cell type information is available
        if isinstance(self.seg.cell_types, pd.DataFrame):
            self.cell_type_combo.clear()
            for cell_type in self.seg.cell_types.columns:
                self.cell_type_combo.addItem(cell_type)

    
    def color_genes(self, gene):
        """Sets object color by selected gene"""
        import numpy as np
        from sklearn.preprocessing import minmax_scale
        from vispy.color.colormap import MatplotlibColormap

        values = self.seg.gene_expression[gene].values
        values = np.log1p(values)
        values = minmax_scale(values)
        cmap = MatplotlibColormap("inferno")
        colors = cmap[values]
        self.viewer.layers[self.seg.__repr__()].color = dict(
            zip(
                self.seg.gene_expression.index,
                colors.rgba
            )
        )
        # Change blending to additive to allow black objects to disapear
        self.viewer.layers[self.seg.__repr__()].blending = "additive"

    def color_cell_type(self, cell_type):
        """Sets object color by selected gene"""
        import numpy as np
        from sklearn.preprocessing import minmax_scale
        from vispy.color.colormap import MatplotlibColormap

        values = self.seg.cell_types[cell_type].values
        values = np.log1p(values)
        values = minmax_scale(values)
        cmap = MatplotlibColormap("inferno")
        colors = cmap[values]
        self.viewer.layers[self.seg.__repr__()].color = dict(
            zip(
                self.seg.cell_types.index,
                colors.rgba
            )
        )
        # Change blending to additive to allow black objects to disapear
        self.viewer.layers[self.seg.__repr__()].blending = "additive"

    def color_reset(self):
        """Reset object color to auto and translucent."""
        self.viewer.layers[self.seg.__repr__()].color_mode = "auto"
        self.viewer.layers[self.seg.__repr__()].blending = "translucent"


if __name__ == "__main__":
    app = QApplication(sys.argv)

    demo = loadImageWidget("dataset", "viewer")
    demo.show()

    sys.exit(app.exec_())
