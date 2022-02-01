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
# d1.load_gene_expression()
d1.images["Cytoplasm"] = d1.images["Cytoplasm"][4000:6000, 5000:6000]

d1.images["Nuclei"] = d1.images["Nuclei"][4000:6000, 5000:6000]

# plt.imshow(d1.images["Nuclei"])
# plt.show()
seg = SegmentCytoplasm(size=120, flow_threshold=0.4, mask_threshold=0)
d1.run_segmentation(seg)

viewer = napari.Viewer(axis_labels=["Dorsoventral", "Mediolateral"])

viewer.add_image(d1.images["Nuclei"], name="Nuclei", colormap="yellow")
viewer.add_image(d1.images["Cytoplasm"], name="Cytoplasm", blending="additive", colormap="cyan")


viewer.add_labels(d1.segmentation.objects)
napari.run()
