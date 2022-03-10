from cellpose import models
from PyQt5.QtCore import QObject, pyqtSignal
import imageio
import pandas as pd
import numpy as np

from typing import Tuple

from utility import select_file


class Communicate(QObject):
    """signals from datastructures"""

    segmentation_list_changed = pyqtSignal()
    active_segmentation_changed = pyqtSignal()
    genes_mapped = pyqtSignal()
    cell_types_changed = pyqtSignal()


class Dataset:

    all = {}

    def __init__(self, name):
        """Creates an experimental dataset.

        name: Name of the dataset
        """
        # Assign information about dataset
        self.name: str = name

        # Create datastructures
        self.images: dict[str, np.ndarray] = dict()
        self.gene_expression: pd.DataFrame = None

        # Note, these are now added from the segmentation class
        self.segmentation: dict[int, Segmentation] = dict()
        self.active_segmentation: Segmentation = None

        # Translate is changed by the crop method
        self.translate = (0, 0)

        # Add dataset to class dictionary
        self.all[name] = self

        # instantiate communicator object
        self.com: Communicate = Communicate()

    def load_nuclei(self, path=False):
        """load nuclei image and store under images["Nuclei"]"""
        if not path:
            path = select_file(title="Please select a nuclei image")

        image = imageio.imread(path)
        self.images["Nuclei"] = image

    def load_cytoplasm(self, path=False):
        """load cytoplasm image and store under images["Cytoplasm"]"""
        if not path:
            path = select_file(title="Please select a cytoplasm image")

        image = imageio.imread(path)
        self.images["Cytoplasm"] = image

    def load_other_channel(self, channel="other", path=False):
        """load channel image and store under images[channel]"""
        if not path:
            path = select_file(title=f"Please select a {channel} image")

        image = imageio.imread(path)
        self.images[channel] = image

    def load_gene_expression(self, path=False):
        """Loads gene expression file"""
        if not path:
            path = select_file(
                title="Please select a csv containing gene expression data"
            )

        df = pd.read_csv(path)

        # TODO Add interface to manually supply which columns that represent
        #  x, y and gene_name
        # Currently this is hard coded bellow. We might want to add more
        # columns such as confident scores etc
        # in the future
        df = df[["PosX", "PosY", "Gene"]]
        df.columns = ["x", "y", "gene"]

        self.gene_expression = df

    def add_segmentation(self, seg: "Segmentation"):
        """add segmentation to the end of list"""
        self.segmentation[seg.id] = seg
        self.com.segmentation_list_changed.emit()

    def remove_segmentation(self, seg: "Segmentation"):
        """remove segmentation at specificed index in list"""
        self.segmentation.pop(seg.id)
        self.com.segmentation_list_changed.emit()

    def crop(
        self, center: Tuple[float, float], width: int = 1000, height: int = 1000
    ) -> "Dataset":
        """returns a cropped version of the dataset
        with added information about the cropping"""

        # Create the new dataset to cold the cropped data
        dataset = Dataset(name=f"cropped {self.name}")

        # Calculate the bounding box coordinates of the crop
        x0, x1 = (int(center[0] - (width / 2)), int(center[0] + (width / 2)))
        y0, y1 = (int(center[1] - (height / 2)), int(center[1] + (height / 2)))

        # Store cropping information
        dataset.center = center
        dataset.width = width
        dataset.height = height
        dataset.boundingbox = (x0, x1, y0, y1)
        dataset.translate = (x0, y0)

        # Cropping images
        for name, image in self.images.items():
            dataset.images[name] = image[x0:x1, y0:y1].copy()

        # Cropping genes
        if isinstance(self.gene_expression, pd.DataFrame):
            idx = list()
            for i, gene in self.gene_expression.iterrows():
                if gene.x > x0 and gene.x <= x1:
                    if gene.y > y0 and gene.y <= y1:
                        idx.append(i)

            df = self.gene_expression.iloc[idx].copy()
            df.x = df.x - x0
            df.y = df.y - y0
            dataset.gene_expression = df

        return dataset

    def set_active_segmentation(self, segmentation: "Segmentation"):
        self.active_segmentation = segmentation
        self.com.active_segmentation_changed.emit()


# Class to make segmentation of image and integrate object related data


class Segmentation:
    _id = 0

    def __init__(self, dataset: Dataset, type: str, settings: dict = dict()):
        self.set_id()
        self.dataset = dataset
        self.type = type
        self.settings = dict()
        self.gene_expression: pd.DataFrame = None
        self.cell_types: pd.DataFrame = None

    def set_id(self):
        """Run to set next available ID of segmentation"""
        # Set unique ID
        self.id = Segmentation._id
        Segmentation._id += 1

    def __repr__(self):
        return f"id:{self.id} type:{self.type}, settings:{self.settings}"

    def run(self):
        """Segment image and return the segmentation object"""
        pass

    def map_genes(self):
        """map genes to segmented objects.
        return: gene expression matrix under self.gene_expression"""
        gene_map = list()
        for i, gene in self.dataset.gene_expression.iterrows():
            object_id = self.objects[int(gene.y), int(gene.x)]
            gene_map.append((gene.gene, object_id, 1))

        df = pd.DataFrame(gene_map, columns=["gene", "object_id", "value"])
        df = df.pivot_table(
            index="object_id", columns="gene", values="value", fill_value=0, aggfunc=sum
        )

        # Store genes mapping to objects
        self.gene_expression = df.iloc[1:]
        # Store genes mapping to background
        self.background = df.iloc[0]

        # broadcast that genes are mapped
        self.dataset.com.genes_mapped.emit()

    def add_cell_types(self, cell_types: pd.DataFrame):
        self.cell_types = cell_types
        self.dataset.com.cell_types_changed.emit()


class segmentNuclei(Segmentation):
    """Segment an image base on nuclei signal
    Stores segmentation under self.objects"""

    def __init__(self, dataset, size=70, flow_threshold=0.4, mask_threshold=0):
        super().__init__(dataset=dataset, type="Cellpose - Nuclei")
        # set attributes
        self.settings = dict(
            size=size, flow_threshold=flow_threshold, mask_threshold=mask_threshold
        )
        self.size = size
        self.flow_threshold = flow_threshold
        self.mask_threshold = mask_threshold

    def run(self):
        model = models.Cellpose(model_type="nuclei")
        masks, flows, styles, diams = model.eval(
            self.dataset.images["Nuclei"],
            diameter=self.size,
            flow_threshold=self.flow_threshold,
            mask_threshold=self.mask_threshold,
        )

        self.objects = masks

        self.dataset.add_segmentation(self)


class segmentCytoplasm(Segmentation):
    """Segment an image base on nuclei and cytoplasm signal
    Stores segmentation under self.objects"""

    def __init__(self, dataset, size=120, flow_threshold=0.4, mask_threshold=0):
        super().__init__(dataset=dataset, type="Cellpose - Cytoplasm")
        # set attributes
        self.settings = dict(
            size=size, flow_threshold=flow_threshold, mask_threshold=mask_threshold
        )
        self.size = size
        self.flow_threshold = flow_threshold
        self.mask_threshold = mask_threshold

    def run(self):
        """segment image using nuclei information"""
        import numpy as np

        n = self.dataset.images["Nuclei"]
        c = self.dataset.images["Cytoplasm"]

        # Stack nuclei and cytoplasm images into a channel image
        arr = np.dstack((n, c))
        model = models.Cellpose(model_type="cyto")
        masks, flows, styles, diams = model.eval(
            x=arr,
            channels=[2, 1],
            diameter=self.size,
            flow_threshold=self.flow_threshold,
            mask_threshold=self.mask_threshold,
        )

        self.objects = masks

        self.dataset.add_segmentation(self)
