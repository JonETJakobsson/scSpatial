from dataset import Dataset
from main_widget import mainWidget
import logging
import napari

logging.basicConfig(level=logging.DEBUG)


class App:
    """
    This app opens napari and load the main widget.

    """

    def __init__(self):

        # Instatiate the empty dataset and viewer objects
        dataset = Dataset("scSpatial experiment")
        viewer = napari.Viewer(axis_labels=["Dorsoventral", "Mediolateral"])

        # Load the docked widget and pass in the dataset and viewer
        viewer.window.add_dock_widget(mainWidget(dataset, viewer), name="scSpatial", add_vertical_stretch=False)

        viewer.show()
        napari.run()


app = App()
