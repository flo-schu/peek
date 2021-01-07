# ======= motion analysis to build a database for object detection ============
# this would be a task for a hyperparameter optimization ()

# 1. LOAD SERIES OBJECT FROM PICKLE (ONLY after images have been preprocessed)
from IPython import get_ipython
from matplotlib import pyplot as plt
import pickle
from image.analysis import Annotations

path = "../data/pics/20201217/"
nano = 42

with open(path+str(nano)+"/series.pkl","rb") as f:
    s = pickle.load(f)

diffs, contours, tagged_ims = s.motion_analysis(lag=1, smooth=12, thresh_binary=15, thresh_size=5)
# s.save_list(tagged_ims, "tagged")

# 2. ANNOTATION
# saving is done automatically

# magic IPython line command
get_ipython().run_line_magic('matplotlib', 'TkAgg')

i = s.images[2]
a = Annotations(i)

# annotate image with keys as displayed in keymap by pressing keys
# n - next image
# b - previous image
a.keymap

i.read_something_from_file('tags')
a.read_tags()
a.show_tag_number(0)

# improvements:
# + TODO: only show not annotated images
# + TODO: option to change the bounding box
#
# Based on this, a two step workflow can be developed:
# 1. Selection on classifying objects this should capture rather too many than too few
#    This can be based on motion detection or any other detector
# 2. classification to differentiate between D/C/N


