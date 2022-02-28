from scanpy import AnnData
from dataset import Segmentation
import bone_fight as bf
import logging
import pandas as pd
import numpy as np


class Bonefight:
    def __init__(self, segmentation: Segmentation, reference: AnnData, groupby:str):
        """perform label transfer from reference to the segmentation.
        
        groupby: key in AnnData.obs containing cell type annotation
        """
        self.segmentation = segmentation
        self.reference = reference
        self.groupby = groupby

    def transfer_labels(self):
        # group by key and calculate mean gene expression
        self.reference_mean = self.groupby_mean()

        # Find intersecting genes
        self.intersecting_genes = self.find_intersecting_genes()

        # Predict labels
        return self.predict()

    def groupby_mean(self) -> pd.DataFrame:
        logging.info("finding mean gene expression per group")

        data = self.reference.X.T
        idx = self.reference.var_names
        col = self.reference.obs_names

        df = pd.DataFrame(data, index=idx, columns=col)

        result = df.groupby(by=self.reference.obs[self.groupby], axis=1).mean()

        return result

    def find_intersecting_genes(self) -> set:
        logging.info("Finding intersecting genes")

        self.reference_genes = set(self.reference_mean.index)
        self.target_genes = set(self.segmentation.gene_expression.columns)

        intersect_genes = self.target_genes.intersection(self.reference_genes)

        return intersect_genes

    def create_reference_view(self):
        self.reference_volume = self.reference.obs[self.groupby].value_counts(sort=False)[self.reference_mean.columns]
        self.reference_volume = self.reference_volume.to_numpy()
        self.reference_filtered = self.reference_mean.filter(self.intersecting_genes, axis=0)
        self.reference_tensor = self.reference_filtered.to_numpy().T
        self.a = bf.View(self.reference_tensor, self.reference_volume)
        

    def create_target_view(self):
        
        self.target_tensor = self.segmentation.gene_expression.filter(self.intersecting_genes, axis=1)
        self.target_tensor = self.target_tensor.to_numpy()
        self.b = bf.View(self.target_tensor, np.ones(self.target_tensor.shape[0]))
       

    def predict(self):
        # TODO: add parameters for this
        self.create_reference_view()
        self.create_target_view()

        self.model = bf.BoneFight(self.a, self.b).fit(200, 0.1)
        self.labels = np.eye(self.reference_tensor.shape[0])
        y = self.model.transform(self.labels)

        cell_types = pd.DataFrame(y, columns=self.reference_filtered.columns, index = self.segmentation.gene_expression.index)
        return cell_types