# Class represening raw dataset
from typing import Tuple

import imageio
import pandas as pd

from utility import select_file


class Dataset:

    all = {}

    def __init__(self, name):
        """Creates an experimental dataset.

        name: Name of the dataset
        """
        # Assign information about dataset
        self.name = name

        # Create datastructures
        self.images = dict()
        self.gene_expression = None

        # Note, these are now added from the segmentation class
        self.segmentation = list()

        # Translate is changed by the crop method
        self.translate = (0, 0)

        # Add dataset to class dictionary
        self.all[name] = self

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

    def crop(
        self,
        center: Tuple[float, float],
        width: int = 1000,
        height: int = 1000
    ) -> "Dataset":
        """returns a cropped version of the dataset
        with added information about the cropping"""

        # Create the new dataset to cold the cropped data
        dataset = Dataset(name=f"cropped {self.name}")

        # Calculate the bounding box coordinates of the crop
        x0, x1 = (int(center[0]-(width/2)), int(center[0]+(width/2)))
        y0, y1 = (int(center[1]-(height/2)), int(center[1]+(height/2)))

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
