# ======= motion analysis to build a database for object detection ============
# this would be a task for a hyperparameter optimization ()

import pandas as pd
from image.process import Series
from image.analysis import Annotations
from utils.manage import Files
import os

path = "../data/pics/"
date = "20210114"
copy_to = "../data/annotations/"
stop_after=100

nanos = [f for f in Files.find_subdirs(os.path.join(path, date)) if f != "999"]


z = 0
for n in nanos:
    s = Series(os.path.join(path, date, n))

    diffs, contours, tagged_ims = s.motion_analysis(lag=1, smooth=12, thresh_binary=15, thresh_size=5)

    for i in s.images[1:]:
        a = Annotations(i, 'motion_analysis', tag_db_path="")
        a.read_new_tags(pd.DataFrame(i.new_tags))

    print("tagged nano {} from {}".format(z, len(nanos)))
    z += 1
    
    Files.copy_files(os.path.join(path, date, n), os.path.join(copy_to, date, n), ex1='.tiff', ex2="PNAN")
    
    if z == stop_after:
        break
    
# Next Steps:
# - [x] Loop over all nanocosms and get tags
# - [x] at the moment avoid executing motion analysis after tagging, because 
#       old tags overwritten!!!
#       This could be resolved with try load tags before reading and 
#       retaining those which have been annotated. Unannotated duplicates could then be
#       discarded. Was resolved by saving annotated tags to a separate DB
# - [x] Write functions to collect 
#       - [x] all tags from one id
#       - [x] all tags from one session
# - [ ] Important: Write detector for Culex
# - [ ] what about zero sized images?
# - [ ] Address memory problems when six images were taken from one nanocosm (need 1.2 GB
        # memory)