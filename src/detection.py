import os
import pandas as pd
from utils.manage import Files
from image.process import Image
from image.analysis import Annotations
from image.detectors.movement_edge import MovementEdgeDetector

# set nanocosm 
path = "../data/pics/"
copy_to = "../data/annotations/"
date = "20210204"
n = "10"

# load images
img1 = Image(os.path.join(path, date, n, "091544"))
img2 = Image(os.path.join(path, date, n, "091548"))

# initialize detector
detector = MovementEdgeDetector()

# tag image
tags = detector.tag_image(
    img1.img, img2.img, 
    dect_args={'blur':5, 'thresh':10}, 
    parfile="../settings/masking_20210225.json",
    search_radius=50)

# export tags
a = Annotations(img1, 'moving_edge', tag_db_path="")
a.read_new_tags(pd.DataFrame(tags.__dict__))
Files.copy_files(os.path.join(path, date, n), os.path.join(copy_to, date, n), 
                 ex1='.tiff', ex2="PNAN")


# to customize it is recommended to write a new detector class under 
# image.detectors in the same style as motion and movement_edge
# then only a new detector has to be initialized
# this script can also be worked on a cluster very well. Nice and scalable
