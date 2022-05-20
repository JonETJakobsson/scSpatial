# SpatialOmics
This software aims to allow analysis of spatial omics data by integrating segmentation methods and information transfer methods in a graphical UI.

## What can I do?
Interactions with your images are allowed by the multi dimentional image viewer [Napari](https://napari.org/). This package adds on a backend that handles the images and gene expression data and this is controlled with a widget in the Napari viewer.

## 1. Segmentation
For high resolution gene expression analysis, where the exact position of a gene is known (such as in [HybISS](https://pubmed.ncbi.nlm.nih.gov/32990747/)), segmentation of the cells are critical to allow cell level analysis of gene expression. We include several options for cell segmentation:

*   Segmentation using Cellpose (nuclei)
*   Segmentation using Cellpose (cytoplasm)
*   Loading of 3rd party segmentation

[Cellpose](http://www.cellpose.org/) can be used with data including onle nuclei staining or images with both nclei and cytoplsm markers. Note that for high gene mapping percentages, cytoplasm markers are prefered!

## 2. Information transfer

# Getting started
Create an environment in using the file [Environment file](environment.yml). This is done using the command `conda env create -f environment.yml`. Should you have to reinstall this environment, like after the environment file has been changes, run `conda env create -f environment.yml --force`

Activate the environment using `conda activate scSpatial`.

To start napari with the scSpatial widget, run the file Run.py `python Run.py`

# Testing code
You can test your code at the end of the module you are working on using an if statment checking if the file is runned, or if it is just loaded. used the code

    if __name__ == "main":
        Do this

