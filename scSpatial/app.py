from dataset import Dataset
from viewer import Viewer
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
        self.dataset = Dataset("scSpatial experiment")
        self.viewer = Viewer(
            title="scSpatial",
            axis_labels=["Dorsoventral", "Mediolateral"]
        )

        # Load the docked widget and pass in the dataset and viewer
        self.viewer.window.add_dock_widget(
            widget=mainWidget(self.dataset, self.viewer),
            name="scSpatial",
            add_vertical_stretch=False
        )

        self.viewer.show()
        napari.run()


app = App()
