# ======= motion analysis to build a database for object detection ============
# this would be a task for a hyperparameter optimization ()

# 1. LOAD SERIES OBJECT FROM PICKLE (ONLY after images have been preprocessed)
from IPython import get_ipython
from image.process import Series
from image.analysis import Annotations
from matplotlib import pyplot as plt

path = "../data/pics/20201217/"
nano = 24

s = Series(path+str(nano))

diffs, contours, tagged_ims = s.motion_analysis(lag=1, smooth=12, thresh_binary=15, thresh_size=5)
# s.save_list(tagged_ims, "tagged")

# 2. ANNOTATION
# saving is done automatically

# magic IPython line command
# %matplotlib
get_ipython().run_line_magic('matplotlib', 'inline')

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


# 1. 

cont=i.tags['contours']

dict(enumerate(cont))
cont[0][0]

def store_contours(self, contours):
    conts = {}
    for i, obj in enumerate(cont):
        conts.update({i:{}})
        for j, coordinate in enumerate(obj):
            conts[i].update({j:{}})
            for ax, val in zip(("x","y"),coordinate[0]):
                conts[i][j].update({ax:val})
    
    # for better human readability
    pd.DataFrame(conts).to_csv('contours.csv', index=False)
    # better machine readability
    json.dumps()

import pandas as pd
import json


cs.iloc[0,0]

test=pd.read_csv('test.csv')
test.iloc[0,0]
dict(test.iloc[0,1])