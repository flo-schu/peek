# ======= motion analysis to build a database for object detection ============
# this would be a task for a hyperparameter optimization ()

import pandas as pd
from image.process import Series
from image.analysis import Annotations

path = "../data/pics/20201217/"
nano = 22

s = Series(path+str(nano))

diffs, contours, tagged_ims = s.motion_analysis(lag=1, smooth=12, thresh_binary=15, thresh_size=5)

for i in s.images[1:3]:
    a = Annotations(i, 'motion_analysis')
    a.read_new_tags(pd.DataFrame(i.new_tags))


# Next Steps:
# 1. Loop over all nanocosms and get tags
# 2. at the moment avoid executing motion analysis after tagging, because 
#    old tags overwritten!!!
#    This could be resolved with try load tags before reading and 
#    retaining those which have been annotated. Unannotated duplicates could then be
#    discarded
# 3. Write functions to collect 
#    - all tags from one id
#    - all tags from one session
# 4. write functions to plot the timeseries (Then I have at least the performance of 
#    Daphnia)
# 5. Important: Write detector for Culex