from img_proc import Series, Image
from rawpy import rawpy
from matplotlib import pyplot as plt
import imageio
path = "../../data/pics/20201203/Serienbilder043/"

s = Series(path)
s.read_images()

# this would be a task for a hyperparameter optimization ()
diffs, contours, tagged_ims = s.motion_analysis(lag=1, smooth=12, thresh_binary=15, thresh_size=5)
# s.save_list([i.img for i in s.images], "ims")
s.save_list(tagged_ims, "tagged_l2")

# improvements for thursday
# 1. take photos with timer and avoid any movement (light, erschütterungen)
# 2. longer time between consecutive fotos should allow also for movement of culex

# moving on:
# FIXES:
# lag 2 does not work yet. There is a shadow which is also tracked. Why?

# 1. write algorithm which builds annotated database
# display picture, context, and choose with key button
# D: Daphnia
# K: Culex
# B: Neither nor

# Based on this, a two step workflow can be developed:
# 1. Selection on classifying objects this should capture rather too many than too few
#    This can be based on motion detection or any other detector
# 2. classification to differentiate between D/C/N
