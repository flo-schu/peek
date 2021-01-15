# ======= annotation of prepared tags ============

from IPython import get_ipython
from image.process import Image, Series
from utils.manage import Files
from image.analysis import Annotations
from matplotlib import pyplot as plt
import os

path = "../data/pics/"
copy_to="../data/annotations"
date = "20201229"
nano = 41

# open image and attributes
# i = Image(path+"21/184248/PNAN2092.tiff")
# open existing anotations and tags
# i.read_struct()

# open series and load image
s = Series(os.path.join(path,date,str(nano)))
i = s.images[1]

keymap = {
    'd':"Daphnia Magna",
    'c':"Culex Pipiens, larva",
    'p':"Culex Pipiens, pupa",
    'u':"unidentified",
}
a = Annotations(i, 'motion_analysis', tag_db_path="../data/tag_db.csv", keymap=keymap)
a.load_processed_tags()

%matplotlib
a.start()
a.show_tag_number(62)

# store annotated tags
Files.copy_files(os.path.join(path, date, str(nano)), os.path.join(copy_to, date, str(nano)), ex1='.tiff', ex2="PNAN")







# help
# annotate image with keys as displayed in keymap by pressing keys
# n - next image
# b - previous image
# other keys as specified in keymap



# Next Steps
# - [x] collect tags (same objective as in motion_analysis.py)
#       - this should be run after the labelling in order to 
#         store labelled images in a secure spot where they
#         cannot be overwritten.
# - [/] only show not annotated images
# - [ ] train object detection algorithm for Daphnia/Culex
# - [ ] option to change the bounding box
# 