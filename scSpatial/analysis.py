
from tokenize import group
from scanpy import AnnData
from dataset import Segmentation
import bone_fight as bf

class Bonefight:
    def __init__(self, segmentation: Segmentation, reference: AnnData, groupby:str):
        """perform label transfer from reference to the segmentation.
        
        groupby: key in AnnData.obs containing cell type annotation
        """
        self.segmentation = segmentation
        self.reference = reference
        self.groupby = groupby

    def transfer_labels(self):
        print("Running bone fight analysis")