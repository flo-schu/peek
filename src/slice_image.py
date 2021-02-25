# ======= motion analysis to build a database for object detection ============
# this would be a task for a hyperparameter optimization ()

import os
from image.process import Series, Image
from image.analysis import Mask
from utils.manage import Files
from matplotlib import pyplot as plt

path = "../data/pics/"
date = "20210204"

s = Series(os.path.join(path, date, "7"))

# img = Image(os.path.join(path, date, "8", "091155"))
# img = Image(os.path.join(path, date, "7", "091355"))
# img = Image(os.path.join(path, date, "6", "090953"))
# img = Image(os.path.join(path, date, "12", "091920"))
# img = Image(os.path.join(path, date, "10", "091544"))
img = Image(os.path.join(path, date, "11", "091732"))

masks = Mask(img.img)
masks.create_masks(pars="../settings/masking_20210225.json")
plt.imshow(masks.img)



