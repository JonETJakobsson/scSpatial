# Class to make segmentation of image and integrate object related data
from cellpose import models


class Segmentation:
    def __init__(self, dataset, method, size=120):
        """Segment an image and calculate features for the segmented objects

        Arguments:
        dataset: dataset.Dataset: object containing all data
        method: method used to segment the image, available methods are
        cyto, nuclei, squares, hexagons.
        size: cell diameter used by cell pose, or size in pixles of grids.
        """
        # Set variables
        self.dataset = dataset
        self.size = size

        if method == "cyto":
            self.segment_cyto()

        elif method == "nuclei":
            self.segment_nuclei()

        else:
            Exception: "Please use a valid method"

    def segment_cyto(self):
        """segment image using cytoplasm information"""
        model = models.Cellpose(model_type="cyto")
        masks, flows, styles, diams = model.eval(
            self.dataset.images["Cytoplasm"], diameter=self.size
        )

        self.objects = masks

    def segment_nuclei(self):
        """segment image using nuclei information"""
        model = models.Cellpose(model_type="nuclei")
        masks, flows, styles, diams = model.eval(
            self.dataset.images["Nuclei"], diameter=self.size
        )

        self.objects = masks
