from dataset import Dataset
import logging
import napari
import matplotlib.pyplot as plt
from segmentation import SegmentNuclei, SegmentCytoplasm

logging.basicConfig(level=logging.DEBUG)


d1 = Dataset(name="lumbar_1")
d1.load_nuclei()
d1.load_cytoplasm()
# d1.load_other_channel(channel="green")
d1.load_gene_expression()
df = d1.gene_expression

idx = list()
for i, gene in df.iterrows():
    if gene.x > 6000 and gene.x <= 8000:
        if gene.y > 5000 and gene.y <= 6000:
            idx.append(i)
df = df.iloc[idx]
df.x = df.x - 6000
df.y = df.y - 5000
df
d1.images["Cytoplasm"] = d1.images["Cytoplasm"][5000:6000, 6000:8000]

d1.images["Nuclei"] = d1.images["Nuclei"][5000:6000, 6000:8000]

seg = SegmentCytoplasm(size=120, flow_threshold=0.4, mask_threshold=0)
seg.run(d1)

viewer = napari.Viewer(axis_labels=["Dorsoventral", "Mediolateral"])

viewer.add_image(d1.images["Nuclei"], name="Nuclei", colormap="yellow")
viewer.add_image(
    d1.images["Cytoplasm"], name="Cytoplasm", blending="additive", colormap="cyan"
)

viewer.add_points(data=list(zip(df.y, df.x)), properties=df, text="Gene")

viewer.add_labels(d1.segmentation[0].objects)
napari.run()
