# class that controls start of napari and integration of back end data.
from widgets import colorObjectWidget
class App:
    """
    This app opens napari and allow loading of files and running analysis.
    
    """
    def __init__(self):
        from dataset import Dataset
        import logging
        import napari
        import matplotlib.pyplot as plt
        from segmentation import SegmentNuclei, SegmentCytoplasm

        logging.basicConfig(level=logging.DEBUG)


        # Assigning the class Dataset to the variable d1 /KM
        d1 = Dataset(name="lumbar_1")
        # Loading Nuclei and Cytoplasm images and storing(is it storing them?) them in d1 /KM
        d1.load_nuclei()
        d1.load_cytoplasm()
        # d1.load_other_channel(channel="green")
        d1.load_gene_expression()
        # Assigning the gene expression information in variable df/dataframe(?) /KM
        df = d1.gene_expression

        # Creating a list called idx /KM
        idx = list()
        # For loop, goes through the genes in each row of our data and all genes that fit the coordinates critera will be put into list idx /KM
        for i, gene in df.iterrows():
            if gene.x > 6000 and gene.x <= 8000:
                if gene.y > 5000 and gene.y <= 6000:
                    idx.append(i)
        # iloc lets us choose a specific location/cell in our list. Subtracting specific values from the X and Y coordinates /KM
        df = df.iloc[idx]
        df.x = df.x - 6000
        df.y = df.y - 5000
        d1.gene_expression = df

        # Altering our cytoplasm and nuclei images to the same coordinates that we have in our gene list /KM
        d1.images["Cytoplasm"] = d1.images["Cytoplasm"][5000:6000, 6000:8000]

        d1.images["Nuclei"] = d1.images["Nuclei"][5000:6000, 6000:8000]

        # Running the segmentation process which is defined in the segmentation.py code, setting our own values /KM
        seg = SegmentCytoplasm(size=120, flow_threshold=0.4, mask_threshold=0)
        seg.run(d1)

        # map genes for segmentation
        seg.map_genes(d1)

        # Choosing Napari as the program we want to look in, labeling our axis, adding our images and assigning color to them. The genes are added as dots and the gene name is added as text /KM
        viewer = napari.Viewer(axis_labels=["Dorsoventral", "Mediolateral"])

        viewer.add_image(d1.images["Nuclei"], name="Nuclei", colormap="yellow")
        viewer.add_image(
            d1.images["Cytoplasm"], name="Cytoplasm", blending="additive", colormap="cyan"
        )

        viewer.add_points(data=list(zip(df.y, df.x)), properties=df, text="gene")

        viewer.add_labels(d1.segmentation[0].objects)
        viewer.window.add_dock_widget(colorObjectWidget(d1, viewer))

        viewer.show()
        napari.run()


    # def run(self):
    #     import napari
    #     self.viewer = napari.Viewer(title="scSpatial")
    #     self.viewer.window.add_dock_widget(colorObjectWidget)
    #     self.viewer.show()
    #     napari.run()


app = App()
