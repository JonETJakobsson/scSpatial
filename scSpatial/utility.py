import numpy
import imageio


def select_file(title: str) -> str:
    """Opens a file select window and return the path to selected file"""
    import tkinter as tk
    from tkinter import filedialog

    root = tk.Tk()
    root.withdraw()

    file_path = filedialog.askopenfilename(title=title)

    return file_path


def open_image(channel: str = None) -> numpy.ndarray:
    """Reads an image with Imageio and run the image in Napari"""
    import napari

    path = select_file(title=channel)
    image = imageio.imread(path)
    viewer = napari.Viewer(show=True)
    viewer.add_image(image, name=channel)
    napari.run()


if __name__ == "__main__":
    open_image("Dapi")
