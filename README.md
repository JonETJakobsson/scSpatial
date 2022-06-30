[![PyPI version](https://badge.fury.io/py/scSpatial.svg)](https://badge.fury.io/py/scSpatial)

# scSpatial
This software aims to allow analysis of 2D spatial transcriptomics data by integrating segmentation methods and information transfer methods in a graphical UI. Interactions with your images are allowed by the multi dimentional image viewer [Napari](https://napari.org/). This package provides segmentation  of the cells and mapping of gene expression data. This is controlled by a widget in the Napari viewer.

## 1. Segmentation
For high resolution gene expression analysis, where the exact position of a gene is known (such as in [HybISS](https://pubmed.ncbi.nlm.nih.gov/32990747/)), segmentation of the cells are critical to allow cell level analysis of gene expression. We include several options for cell segmentation:

*   Segmentation using Cellpose (nuclei)
*   Segmentation using Cellpose (cytoplasm)
*   Loading of 3rd party segmentation (ImageJ, Ilastik, CellProfiler etc.)

[Cellpose](http://www.cellpose.org/) can be used with data including only nuclei staining or images with both nuclei and cytoplasm markers. To achive high gene mapping ratios, segmentation using cytoplasm markers are prefered! When loading 3rd party segmentation images, these should have unique pixel values for each object in the segmentation, with the value 0 reserved for background.

## 2. Information transfer
With a segmented image, it is possible to map genes to objects (cells) creating a table with gene expression for each object. This information is similar to the data in scRNA-seq datasets, and information transfer between a reference dataset and the spatial mapping can be performed using the [Tangram](https://www.nature.com/articles/s41592-021-01264-7) method. Here we have implemented the [BoneFight](https://github.com/linnarsson-lab/BoneFight) modification from Linnarssons lab which allows for cell cluster based computation.

## 3. Visualization
Currently, we support visualization of gene expression and cell type prediction. This section will be expanded as new tools are implemented.

# Getting started
## Installation
Install Miniconda or Anaconda and create a virtual environment with python 3.7 and activate it.
```bash
conda create -n scSpatial python=3.7
conda activate scSpatial
```
Install scSpatial using pip:
 ```
 pip install scSpatial
 ```
 
 Next we install some dependencies that are not available via pip:
```bash
pip install git+https://github.com/linnarsson-lab/BoneFight.git@8c1ec1f
pip install git+https://github.com/linnarsson-lab/loompy.git@e0963fb
```
## Running napari with the scSpatial widget
To open Napari with the scSpatial widget, run the scSpatial command in the terminal:
```bash
scSpatial
```

If you want to start napari from within your own pipeline/script, import the `scSpatial.app.App` class and instantiate it.

```python
from scSpatial.app import App
app = App()
```

# Change Log

## v0.1.3
- Added Bonefight cell types to segmentation export.
- Fixed bug where Napari would not set propper contrast limits. This is now set using `numpy.min` and `numpy.max` functions explicitly.

## v0.1.2
- Bumped version of cellpose to > 2.0.4
- Removed resample during cell pose model evaluation to speed up segmentation.

## v0.1.1
- Constrained Cellpose to version 1.0.2 as later versions cased errors.

## V0.1.0
Initial release



