import os
import pandas as pd
from utils.manage import Files
from image.process import Image
from image.analysis import Annotations
from image.detectors.movement_edge import MovementEdgeDetector as med

path = "../data/pics/"
copy_to = "../data/annotations/"
date = "20210204"
n = "10"
rad = 50

# load images
img1 = Image(os.path.join(path, date, n, "091544"))
img2 = Image(os.path.join(path, date, n, "091548"))

# mask images
m0 = med.Slice(img2.img)
m1 = med.Slice(img1.img)
m0.create_masks(pars="../settings/masking_20210225.json")
m1.create_masks(pars="../settings/masking_20210225.json")

# determin points of interest
pois = med.find_pois(
    m0.img, m1.img, filter_fun=med.filter_contours, 
    threshold=20, sw=20, erode_n=3)

# initialize tagger
tags = med.DetectSelectSortTagger()
dect_args = {'blur':5, 'thresh':10}
tags.tag_image(m0, m1, pois, med.median_threshold, dect_args, med.pass_tests, 
               search_radius=50)

# export
a = Annotations(img1, 'moving_edge', tag_db_path="")
a.read_new_tags(pd.DataFrame(tags.__dict__))
Files.copy_files(os.path.join(path, date, n), os.path.join(copy_to, date, n), 
                 ex1='.tiff', ex2="PNAN")
