# SpatialOmics
This software aims to allow analysis of spatial omics data by integrating segmentation methods and information transfer methods in a graphical UI. Interactions with your images are allowed by the multi dimentional image viewer [Napari](https://napari.org/). This package provides segmentation  of the cells and mapping of gene expression data. This is controlled by a widget in the Napari viewer.

## 1. Segmentation
For high resolution gene expression analysis, where the exact position of a gene is known (such as in [HybISS](https://pubmed.ncbi.nlm.nih.gov/32990747/)), segmentation of the cells are critical to allow cell level analysis of gene expression. We include several options for cell segmentation:

*   Segmentation using Cellpose (nuclei)
*   Segmentation using Cellpose (cytoplasm)
*   Loading of 3rd party segmentation (ImageJ, Ilastik, CellProfiler etc.)

[Cellpose](http://www.cellpose.org/) can be used with data including only nuclei staining or images with both nuclei and cytoplasm markers. To achive high gene mapping ratios, segmentation using cytoplasm markers are prefered!

## 2. Information transfer
With a segmented image, it is possible to map genes to objects (cells) creating a table with gene expression for each object. This information is similar to the data in scRNA-seq datasets, and information transfer between a reference dataset and the spatial mapping can be performed using the [Tangram](https://www.nature.com/articles/s41592-021-01264-7) method. Here we have implemented the [BoneFight](https://github.com/linnarsson-lab/BoneFight) modification from Linnarssons lab which allows for cell cluster based computation.

## 3. Visualization
Currently, we support visualization of gene expression of cells and cell type prediction. This section will be expanded as new tools are implemented.

# Getting started
Create an environment in using the file [Environment file](environment.yml). This is done using the command `conda env create -f environment.yml`. Should you have to reinstall this environment, like after the environment file has been changes, run `conda env create -f environment.yml --force`

Activate the environment using `conda activate scSpatial`.

To start napari with the scSpatial widget, run the file Run.py `python Run.py`



