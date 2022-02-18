import sys

import imageio
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (QApplication, QComboBox, QFileDialog, QFormLayout,
                             QGridLayout, QHBoxLayout, QLabel, QListWidget,
                             QPushButton, QSlider, QVBoxLayout, QWidget)

from dataset import Dataset
from segmentation import Segmentation, segmentCytoplasm, segmentNuclei
from viewer import Viewer

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
        layout.addWidget(btn_other, 2, 0)

        self.label_nuc = QLabel("")
        layout.addWidget(self.label_nuc, 0, 1)

        self.label_cyto = QLabel("")
        layout.addWidget(self.label_cyto, 1, 1)

        self.label_other = QLabel("")
        layout.addWidget(self.label_other, 2, 1)

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
        seg = Segmentation(type="External")
        seg.objects = masks

        self.dataset.segmentation.append(seg)
        self.viewer.add_segmentation(seg, self.dataset)

    def run_segmentation_test(self):
        _, y, x = self.viewer.camera.center
        crop = self.dataset.crop(center=(y, x))

        size = int(self.lbl_size.text())
        f_th = float(self.lbl_flow_th.text())
        m_th = float(self.lbl_mask_th.text())

        if self.method_combo.currentText() == "Cellpose - Nuclei":
            seg = segmentNuclei(
                size=size,
                flow_threshold=f_th,
                mask_threshold=m_th
            )
        if self.method_combo.currentText() == "Cellpose - Cytoplasm":
            seg = segmentCytoplasm(
                size=size,
                flow_threshold=f_th,
                mask_threshold=m_th
            )

        seg.run(crop)
        self.viewer.add_segmentation(seg, crop)
        # Add segmentation to main dataset segmentation list
        self.dataset.segmentation.append(seg)

    def run_segmentation(self):
        size = int(self.lbl_size.text())
        f_th = float(self.lbl_flow_th.text())
        m_th = float(self.lbl_mask_th.text())

        if self.method_combo.currentText() == "Cellpose - Nuclei":
            seg = segmentNuclei(
                size=size,
                flow_threshold=f_th,
                mask_threshold=m_th
            )
        if self.method_combo.currentText() == "Cellpose - Cytoplasm":
            seg = segmentCytoplasm(
                size=size,
                flow_threshold=f_th,
                mask_threshold=m_th
            )

        seg.run(self.dataset)
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

        # Add a refresh buton to update the list
        # TODO: this should be automatic in the future when
        # ever the segmentation list changes
        self.update_btn = QPushButton("Update list")
        self.update_btn.clicked.connect(self.update_segmentation_list)
        self.layout.addWidget(self.update_btn)

        self.seg_list = QListWidget(self)
        self.layout.addWidget(self.seg_list)

        self.setLayout(self.layout)

    def update_segmentation_list(self):
        self.seg_list.clear()
        if len(self.dataset.segmentation) > 0:
            print("adding")
            for seg in self.dataset.segmentation:
                self.seg_list.addItem(seg.__repr__())


class colorObjectWidget(QWidget):
    """Widget used to color objects by different features
    (currently gene expression)"""

    def __init__(self, dataset, viewer):
        super().__init__()
        self.dataset = dataset
        self.viewer = viewer
        if len(self.dataset.segmentation) > 0:
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
