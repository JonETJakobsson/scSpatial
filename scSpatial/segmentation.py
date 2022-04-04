from cellpose import models
import pandas as pd
import numpy as np
from skimage import measure

from typing import Tuple

#Import only for type hinting
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from .dataset import Dataset

MAX_OBJECTS_SIZE = 3000 # max size of objects image when downsampeling

class Segmentation:
    _id = 0

    def __init__(self, dataset: "Dataset", type: str, settings: dict = dict(), objects: np.ndarray = None):
        self.set_id()
        self.dataset = dataset
        self.objects = objects
        self.type = type
        self.settings = settings
        self.gene_expression: pd.DataFrame = None
        self.background: pd.Series = None
        self.pct_mapped_genes: pd.Series = None
        self.object_coverage: float = None
        self.cell_types: pd.DataFrame = None
        self.downsampled: Tuple[np.ndarray, float] = None # used for gene visualization of large images

        self.run()

        if isinstance(self.dataset.gene_expression, pd.DataFrame):
            self.map_genes()

        self.calculate_object_coverage()
        
        self.calculate_object_features()

        self.downsample()

        self.dataset.add_segmentation(self)

    def set_id(self):
        """Run to set next available ID of segmentation"""
        # Set unique ID
        self.id = Segmentation._id
        Segmentation._id += 1

    def __repr__(self):
        return f"id:{self.id} type:{self.type}, settings:{self.settings}"

    def run(self):
        """Algorithm used to find objects"""
        pass

    def calculate_object_coverage(self):
        """Calculate percent of image covered in objects"""
        object_pixels = sum(sum(self.objects > 0))
        self.object_coverage = object_pixels / (object_pixels + self.objects.size)

    def calculate_object_features(self):
        features: pd.DataFrame = pd.DataFrame(measure.regionprops_table(
            self.objects,
            properties=[
                "label",
                "centroid",
                "area",
                "equivalent_diameter_area"]
        ))
        self.object_features = features
   
    def map_genes(self):
        """map genes to segmented objects.
        self.gene_expression: number of genes mapped to each cell
        self.background: number of genes mapped to backgound
        self.pct_mapped_genes: percent of induvidual genes mapped to cells"""
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

        # Calculate percent of genes mapped to cells
        self.pct_mapped_genes = self.gene_expression.sum() / (self.gene_expression.sum() + self.background)

        # broadcast that genes are mapped
        self.dataset.com.genes_mapped.emit()

    def add_cell_types(self, cell_types: pd.DataFrame):
        self.cell_types = cell_types
        self.dataset.com.cell_types_changed.emit()

    def downsample(self):
        objects = self.objects.copy()
        scale = 1.0
        while objects.shape[0] > MAX_OBJECTS_SIZE or objects.shape[1] > MAX_OBJECTS_SIZE:
            # half the resulotion each run
            objects = objects[::2, ::2]
            scale += scale
        self.downsampled = (objects, scale)


class segmentNuclei(Segmentation):
    """Segment an image base on nuclei signal
    Stores segmentation under self.objects"""

    def __init__(self, dataset, size=70, flow_threshold=0.4, mask_threshold=0):
        # set attributes
        self.settings = dict(
            size=size, flow_threshold=flow_threshold, mask_threshold=mask_threshold
        )
        self.size = size
        self.flow_threshold = flow_threshold
        self.mask_threshold = mask_threshold

        super().__init__(dataset=dataset, type="Cellpose - Nuclei")
        

    def run(self):
        model = models.Cellpose(model_type="nuclei")
        masks, flows, styles, diams = model.eval(
            self.dataset.images["Nuclei"],
            diameter=self.size,
            flow_threshold=self.flow_threshold,
            mask_threshold=self.mask_threshold,
        )

        self.objects = masks


class segmentCytoplasm(Segmentation):
    """Segment an image base on nuclei and cytoplasm signal
    Stores segmentation under self.objects"""

    def __init__(self, dataset, size=120, flow_threshold=0.4, mask_threshold=0):
        # set attributes
        self.settings = dict(
            size=size, flow_threshold=flow_threshold, mask_threshold=mask_threshold
        )
        self.size = size
        self.flow_threshold = flow_threshold
        self.mask_threshold = mask_threshold

        super().__init__(dataset=dataset, type="Cellpose - Cytoplasm")
        

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
