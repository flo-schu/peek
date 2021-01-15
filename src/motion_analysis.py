# ======= motion analysis to build a database for object detection ============
# this would be a task for a hyperparameter optimization ()

import pandas as pd
from image.process import Series
from image.analysis import Annotations
from utils.manage import Files
import os

path = "../data/pics/20201229/"
nanos = [f for f in Files.find_subdirs(path) if f != "999"]

for n in nanos:
    s = Series(os.path.join(path,n))

    diffs, contours, tagged_ims = s.motion_analysis(lag=1, smooth=12, thresh_binary=15, thresh_size=5)

    for i in s.images[1:]:
        a = Annotations(i, 'motion_analysis')
        a.read_new_tags(pd.DataFrame(i.new_tags))

    print("tagged nano {} from {}".format(n, len(nanos)))

# Next Steps:
# - [x] Loop over all nanocosms and get tags
# - [ ] at the moment avoid executing motion analysis after tagging, because 
#       old tags overwritten!!!
#       This could be resolved with try load tags before reading and 
#       retaining those which have been annotated. Unannotated duplicates could then be
#       discarded
# - [ ] Write functions to collect 
#       - [ ] all tags from one id
#       - [ ] all tags from one session
# - [ ] write functions to plot the timeseries (Then I have at least the performance of 
#       Daphnia)
# - [ ] Important: Write detector for Culex