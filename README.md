# SpatialOmics
This software aims to allow analysis of spatial omics data by integrating segmentation methods with information transfer methods.


# Getting started
Create an environment in using the file [Environment file](environment.yml). This is done using the command `conda env create -f environment.yml`. Should you have to reinstall this environment, like after the environment file has been changes, run `conda env create -f environment.yml --force`

Activate the environment using `conda activate scSpatial`.

To start napari with the scSpatial widget, run the file Run.py `python Run.py`

# Testing code
You can test your code at the end of the module you are working on using an if statment checking if the file is runned, or if it is just loaded. used the code

    if __name__ == "main":
        Do this

