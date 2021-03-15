# 1. get directory tree of all 999 subfolders
# 2. read images
# 3. downscale and cut out region where number of nano will be 
# 4. annotate with date, time and img name
# 5. save and label according to date, time and name in one folder
# 6. create CSV file with labels friom (5) in the same order (should be automatic due to date and time format YYYYMMDD_HHMM_NAME.tiff)
#    this should be kept and only updated with new unclear nanos, so that not everything has to be ran twice
# 7. read the file and move images from 999 to appropriate locations

import os

with open("data/image_analysis/qr_check.txt", "r") as f:
    mqr = f.read()