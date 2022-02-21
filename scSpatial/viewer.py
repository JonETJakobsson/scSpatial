import napari
from dataset import Dataset, Segmentation


class Viewer(napari.Viewer):
    """Custom Viewer with methods to add elements to napari
    """

    def add_segmentation(self, seg: Segmentation, dataset: Dataset):
        """Add segmentation to viewer"""
        self.add_labels(
            seg.objects,
            translate=dataset.translate,
            name=seg.__repr__()
        )

    def add_nuclei(self, dataset: Dataset):
        """Add image with key "Nuclei" to viewer"""
        self.add_image(
            dataset.images["Nuclei"],
            name="Nuclei",
            colormap="yellow",
            blending="additive"
        )

    def add_cytoplasm(self, dataset: Dataset):
        """Add image with key "Cytoplasm" to viewer"""
        self.add_image(
            dataset.images["Cytoplasm"],
            name="Cytoplasm",
            colormap="cyan",
            blending="additive"
        )

    def add_other_channel(
        self,
        dataset: Dataset,
        channel: str,
        colormap: str = "magenta"
    ):
        """Add image with given channel to viewer"""
        self.add_image(
            dataset.images[channel],
            name=channel,
            colormap=colormap,
            blending="additive"
        )

    def add_genes(self, dataset: Dataset):
        """Add genes to viewer"""
        from vispy.color.colormap import get_colormap

        cm = get_colormap("gist_rainbow")
        codes = dataset.gene_expression.gene.cat.codes
        colors = cm.map(codes/max(codes))

        text_property = {
            "text": "{gene}",
            "size": 12,
            "color": "white",
            "translation": (-3, 0),
            "visible": False
        }

        self.add_points(
            data=list(zip(
                dataset.gene_expression.y,
                dataset.gene_expression.x
            )),
            properties=dataset.gene_expression,
            name="Genes",
            text=text_property,
            face_color=colors
        )
