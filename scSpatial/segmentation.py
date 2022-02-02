# Class to make segmentation of image and integrate object related data
from cellpose import models


class Segmentation:
    def __init__(self):
        """General segmentation

        methods:
        -------
        self.run(): Runs the segmentation and returns a label image (Mask)
        with unique values for each object.

        """

    def run(self, dataset):
        """Segment image and return the segmentation object"""
        pass


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
        return self


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

        y, x = dataset.images["Cytoplasm"].shape
        arr = np.ndarray((2, y, x))
        arr[0] = dataset.images["Nuclei"]
        arr[1] = dataset.images["Cytoplasm"]

        model = models.Cellpose(model_type="cyto")
        masks, flows, styles, diams = model.eval(
            x=arr,
            channels=[2, 1],
            diameter=self.size,
            flow_threshold=self.flow_threshold,
            mask_threshold=self.mask_threshold,
        )

        self.objects = masks
        return self
