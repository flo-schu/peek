# ======= annotation of prepared tags ============

from IPython import get_ipython
from image.process import Image, Series
from image.analysis import Annotations
from matplotlib import pyplot as plt
import os

path = "../data/pics/20201217/"
nano = 20

# open image and attributes
# i = Image(path+"21/184248/PNAN2092.tiff")
# open existing anotations and tags
# i.read_struct()

# open series and load image
s = Series(path+str(nano))
i = s.images[1]

a = Annotations(i, 'motion_analysis')
a.load_processed_tags()

%matplotlib
a.start()
a.show_tag_number(0)


# help
a.keymap
# annotate image with keys as displayed in keymap by pressing keys
# n - next image
# b - previous image



# Next Steps
# 1. collect tags (same objective as in motion_analysis.py)
# 2. train object detection algorithm for Daphnia/Culex
# 
#  improvements:
# 1. only show not annotated images
# 2. option to change the bounding box
#
#