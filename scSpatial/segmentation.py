# Class to make segmentation of image and integrate object related data
from cellpose import models
from dataset import Dataset
import pandas as pd


class Segmentation:
    _id = 0

    def __init__(self, type: str):
        self.set_id()
        self.type = type
        self.settings = dict()

    def set_id(self):
        """Run to set next available ID of segmentation"""
        # Set unique ID
        self.id = Segmentation._id
        Segmentation._id += 1

    def __repr__(self):
        return f"id:{self.id} type:{self.type}, settings:{self.settings}"

    def run(self, dataset: Dataset):
        """Segment image and return the segmentation object"""
        pass

    def map_genes(self, dataset: Dataset):
        """map genes to segmented objects.
        return: gene expression matrix under self.gene_expression"""
        gene_map = list()
        for i, gene in dataset.gene_expression.iterrows():
            object_id = self.objects[int(gene.y), int(gene.x)]
            gene_map.append((gene.gene, object_id, 1))

        df = pd.DataFrame(gene_map, columns=["gene", "object_id", "value"])
        df = df.pivot_table(
            index="object_id",
            columns="gene",
            values="value",
            fill_value=0,
            aggfunc=sum
        )

        # Store genes mapping to objects
        self.gene_expression = df.iloc[1:]
        # Store genes mapping to background
        self.background = df.iloc[0]


class segmentNuclei(Segmentation):
    """Segment an image base on nuclei signal
    Stores segmentation under self.objects"""

    def __init__(self, size=70, flow_threshold=0.4, mask_threshold=0):
        # set attributes
        self.settings = dict(
            size=size,
            flow_threshold=flow_threshold,
            mask_threshold=mask_threshold
        )
        self.type = "Cellpose - Nuclei"
        self.size = size
        self.flow_threshold = flow_threshold
        self.mask_threshold = mask_threshold

        self.set_id()

    def run(self, dataset: Dataset):
        model = models.Cellpose(model_type="nuclei")
        masks, flows, styles, diams = model.eval(
            dataset.images["Nuclei"],
            diameter=self.size,
            flow_threshold=self.flow_threshold,
            mask_threshold=self.mask_threshold,
        )

        self.objects = masks

        dataset.segmentation.append(self)


class segmentCytoplasm(Segmentation):
    """Segment an image base on nuclei and cytoplasm signal
    Stores segmentation under self.objects"""

    def __init__(self, size=120, flow_threshold=0.4, mask_threshold=0):
        # set attributes
        self.settings = dict(
            size=size,
            flow_threshold=flow_threshold,
            mask_threshold=mask_threshold
        )
        self.type = "Cellpose - Cytoplasm"
        self.size = size
        self.flow_threshold = flow_threshold
        self.mask_threshold = mask_threshold
        self.set_id()

    def run(self, dataset: Dataset):
        """segment image using nuclei information"""
        import numpy as np

        n = dataset.images["Nuclei"]
        c = dataset.images["Cytoplasm"]

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

        dataset.segmentation.append(self)
