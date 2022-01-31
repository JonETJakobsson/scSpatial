# Class represening raw dataset
from utility import select_file
from segmentation import Segmentation
import imageio
import pandas as pd
import napari


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
        self.gene_expression = df

    def run_segmentation(self, method, size):
        self.segmentation = Segmentation(self, method=method, size=size)


if __name__ == "__main__":
    d1 = Dataset(name="lumbar_1")
    d1.load_nuclei()
    # d1.load_cytoplasm()
    # d1.load_other_channel(channel="green")
    d1.load_gene_expression()
    d1.run_segmentation(method="nuclei", size=40)

    napari.view_labels(d1.segmentation.objects)