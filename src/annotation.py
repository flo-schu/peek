# ======= annotation of prepared tags ============

from IPython import get_ipython
from image.process import Image, Series
from image.analysis import Annotations
from matplotlib import pyplot as plt
import os

path = "../data/pics/20201217/"
nano = 23

# open image and attributes
# i = Image(path+"21/184248/PNAN2092.tiff")
# open existing anotations and tags
# i.read_struct()

# open series and load image
s = Series(path+str(nano))
i = s.images[1]

keymap = {
    'd':"Daphnia Magna",
    'c':"Culex Pipiens, larva",
    'p':"Culex Pipiens, pupa",
    'u':"unidentified",
}
a = Annotations(i, 'motion_analysis', keymap)
a.load_processed_tags()

%matplotlib
a.start()
a.show_tag_number(0)


# help
# annotate image with keys as displayed in keymap by pressing keys
# n - next image
# b - previous image
# other keys as specified in keymap



# Next Steps
# 1. collect tags (same objective as in motion_analysis.py)
#    - this should be run after the labelling in order to 
#      store labelled images in a secure spot where they
#      cannot be overwritten.
# 2. train object detection algorithm for Daphnia/Culex
# 
# improvements:
# 1. only show not annotated images
# 2. option to change the bounding box
#
#