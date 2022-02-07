# Class to make segmentation of image and integrate object related data
from cellpose import models
import pandas as pd


class Segmentation:
    def __init__(self):
        """General segmentation

        methods:
        -------
        self.run(Dataset): Runs the segmentation on the dataset. 
        and stores segmentation under self.objects
        """

    def run(self, dataset):
        """Segment image and return the segmentation object"""
        pass


    def map_genes(self, dataset):
        """map genes to segmented objects.
        return: gene expression matrix under self.gene_expression"""
        gene_map = list()
        for i, gene in dataset.gene_expression.iterrows():
            object_id = self.objects[int(gene.y), int(gene.x)]
            gene_map.append((gene.gene, object_id, 1))

        df = pd.DataFrame(gene_map, columns=["gene", "object_id", "value"])
        df = df.pivot_table(index="object_id", columns="gene", values="value", fill_value=0, aggfunc=sum)
        self.gene_expression = df


class SegmentNuclei(Segmentation):
    """Segment an image base on nuclei signal
    Stores segmentation under self.objects"""

    def __init__(self, size=70, flow_threshold=0.4, mask_threshold=0):
        # set variables
        self.size = size
        self.flow_threshold = flow_threshold
        self.mask_threshold = mask_threshold

    def run(self, dataset):
        model = models.Cellpose(model_type="nuclei")
        masks, flows, styles, diams = model.eval(
            dataset.images["Nuclei"],
            diameter=self.size,
            flow_threshold=self.flow_threshold,
            mask_threshold=self.mask_threshold,
        )

        self.objects = masks
        
        dataset.segmentation.append(self)


class SegmentCytoplasm(Segmentation):
    """Segment an image base on nuclei and cytoplasm signal
    Stores segmentation under self.objects"""

    def __init__(self, size=120, flow_threshold=0.4, mask_threshold=0):
        # set variables
        self.size = size
        self.flow_threshold = flow_threshold
        self.mask_threshold = mask_threshold

    def run(self, dataset):
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
