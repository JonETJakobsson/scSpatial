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
from ..segmentation import Segmentation, segmentCytoplasm, segmentNuclei
from ..viewer import Viewer
from ..analysis import Bonefight


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
            ["select method", "Cellpose - Nuclei", "Cellpose - Cytoplasm", "External"]
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
            self.lbl_mask_th.setText(str((self.sldr_mask_th.value() - 60) / 10))
            h3_layout.addWidget(self.sldr_mask_th)
            h3_layout.addWidget(self.lbl_mask_th)
            self.option_layout.addRow("Mask threshold", h3_layout)

            btn_run_test = QPushButton("Test run")
            btn_run_test.setToolTip("Test segmentation, focus on the center for viewer, 1000x1000")
            btn_run_test.clicked.connect(self.run_segmentation_test)

            btn_run = QPushButton("Run")
            btn_run.setToolTip("Run segmentation on entire image")
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
        path = QFileDialog.getOpenFileName(self, caption="select a segmentation file")[
            0
        ]

        masks = imageio.imread(path).astype(int)
        seg = Segmentation(dataset=self.dataset, type="External", objects=masks)
        
        self.viewer.add_segmentation(seg, self.dataset)

    def run_segmentation_test(self):
        _, y, x = self.viewer.camera.center
        crop = self.dataset.crop(center=(y, x))

        size = int(self.lbl_size.text())
        f_th = float(self.lbl_flow_th.text())
        m_th = float(self.lbl_mask_th.text())

        if self.method_combo.currentText() == "Cellpose - Nuclei":
            seg = segmentNuclei(
                dataset=crop, size=size, flow_threshold=f_th, mask_threshold=m_th
            )
        if self.method_combo.currentText() == "Cellpose - Cytoplasm":
            seg = segmentCytoplasm(
                dataset=crop, size=size, flow_threshold=f_th, mask_threshold=m_th
            )

      
        self.viewer.add_segmentation(seg, crop)
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
                mask_threshold=m_th,
            )
        if self.method_combo.currentText() == "Cellpose - Cytoplasm":
            seg = segmentCytoplasm(
                dataset=self.dataset,
                size=size,
                flow_threshold=f_th,
                mask_threshold=m_th,
            )

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
        remove_btn.setToolTip(
            "Remove segmentation from layer list and segmentation list"
        )
        remove_btn.clicked.connect(self.remove_row)
        self.layout.addWidget(remove_btn)

        add_btn = QPushButton("Add to viewer")
        add_btn.setToolTip(
            """Did you accidentally remove a segmentation?
            Press to add it to layer list again"""
        )
        add_btn.clicked.connect(self.add_to_viewer)
        self.layout.addWidget(add_btn)

        set_btn = QPushButton("Set as active segmentation")
        set_btn.setToolTip("Selected segmentation will be used for downstream analysis and visualization")
        set_btn.clicked.connect(self.set_active)
        self.layout.addWidget(set_btn)

        export_btn = QPushButton("Export segmentation")
        export_btn.setToolTip("Exports an excel file with information about mapped genes to objects and background")
        export_btn.clicked.connect(self.export_seg)
        self.layout.addWidget(export_btn)

        seg_info_btn = QPushButton("Show statistics")
        seg_info_btn.setToolTip("Opens a pop-up window with detailed information about segmentation")
        seg_info_btn.clicked.connect(self.open_segmentation_info_window)
        self.layout.addWidget(seg_info_btn)

        self.layout.addStretch()
        self.setLayout(self.layout)

    def remove_row(self):
        row = self.seg_table.currentRow()
        id = self.seg_table.item(row, 0)
        self.viewer.remove_segmentation(seg=self.dataset.segmentation[int(id.text())])
        self.dataset.remove_segmentation(seg=self.dataset.segmentation[int(id.text())])

    def add_to_viewer(self):
        # TODO check if segmentation already is in list
        row = self.seg_table.currentRow()
        id = self.seg_table.item(row, 0)
        self.viewer.add_segmentation(
            seg=self.dataset.segmentation[int(id.text())], dataset=self.dataset
        )

    def set_active(self):
        row = self.seg_table.currentRow()
        id = self.seg_table.item(row, 0)
        self.dataset.set_active_segmentation(self.dataset.segmentation[int(id.text())])
        self.update_segmentation_list()
        for column in range(3):
            item = self.seg_table.item(row, column)
            item.setBackground(QColor(255, 128, 128))

    def export_seg(self):
        row = self.seg_table.currentRow()
        id = self.seg_table.item(row, 0)
        seg = self.dataset.segmentation[int(id.text())]

        path = QFileDialog.getSaveFileName(caption="Save as", filter="Excel File (*.xlsx)")[0]
        writer = pd.ExcelWriter(path)
        seg.gene_expression.to_excel(writer, sheet_name="Gene Expression")
        seg.background.to_excel(writer, sheet_name="Background")
        writer.save()

    def update_segmentation_list(self):
        self.seg_table.clear()
        self.seg_table.setColumnCount(3)

        self.seg_table.setHorizontalHeaderLabels(["ID", "Type", "Settings"])

        if len(self.dataset.segmentation) > 0:
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

    def open_segmentation_info_window(self):
        """Opens a pop-up window with statistics for a selected segmentation"""
        # Fetch selected segmentation
        row = self.seg_table.currentRow()
        id = self.seg_table.item(row, 0)
        seg = self.dataset.segmentation[int(id.text())]

        self.segmentation_info_widget = segmentationInfoWidget(seg)

class segmentationInfoWidget(QWidget):
    def __init__(self, seg: Segmentation):
        super().__init__()
        self.seg = seg
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"{self.seg.__repr__()}")
        self.setGeometry(0, 0, 1500, 10000)
        #Layout is horisontal with info on left and graph on right
        self.layout = QVBoxLayout(self)

        self.info_form_layout = QFormLayout()
        sum_tot = self.seg.gene_expression.sum().sum()
        sum_backgound = self.seg.background.sum()
        total_pct =  sum_tot / (sum_tot + sum_backgound)
        self.info_form_layout.addRow(
            "Percent mapping spots in total:",
            QLabel(f"{round(total_pct*100, 2)}%")
        )

        self.info_form_layout.addRow(
            "Object coverage",
            QLabel(f"{round(self.seg.object_coverage*100, 2)}%")
        )

        # make percent mapped genes plot
        self.gene_bar_chart = QWebEngineView(self)
        self.gene_bar_chart.setGeometry(0, 0, 1000, 500)
        b = px.bar(
            data_frame=self.seg.pct_mapped_genes*100,
            labels={"value": "% spots mapped", "gene": "Genes"}
        )
        html = b.to_html(include_plotlyjs="cdn")
        self.gene_bar_chart.setHtml(html)
        
        self.info_form_layout.addWidget(self.gene_bar_chart)

        self.layout.addLayout(self.info_form_layout)
        self.setLayout(self.layout)
        self.show()
