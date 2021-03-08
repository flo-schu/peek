import cv2 as cv
import os
import numpy as np
import itertools as it
import pandas as pd
from matplotlib import pyplot as plt

from image.process import Series, Image, Tagger
from image.analysis import Mask, Spectral, Detector, Annotations
from evaluation.plot import Viz
from utils.manage import Files

# here I can create my own individual program of functions, that I want to execute
# This is very nice, because here it makes it explicit what is to be done,
# but leaves the overhead out of the way
class Slice(Mask):
    def create_masks(self, pars):
        super().create_masks(pars)

        self.img = self.trim(self.img, **self.pars['trim'])
        self.remove_blue_tape(**self.pars['blue_tape'])
        self.mask_sediment(**self.pars['sediment'])     
        # self.mask_airspace(**self.pars['airspace'])        
        # self.mask_water_surface(**self.pars['water_surface'])

def filter_contours(contours):
    cnts = []
    for c in contours:
        if cv.moments(c)['m01'] / max(1, cv.moments(c)['m10']) > 100:
            pass
        else:
            cnts.append(c)

    return cnts

def median_threshold(roi, blur, thresh):
    median = cv.medianBlur(roi, blur)
    background = Detector.substract_median(median, ignore_value=0)
    gray = cv.cvtColor(background, cv.COLOR_RGB2GRAY)
    T, thresh = cv.threshold(gray, thresh, 255, 0)
    return [roi, median, background, gray, thresh]

def pass_tests(d):
    d['select'] = True
    d['select'] = d['select'] and not d['len_major'] > 500
    d['select'] = d['select'] and not d['len_minor'] > 500
    d['select'] = d['select'] and not d['area'] < 5
    d['select'] = d['select'] and not d['area'] > 5000
    d['select'] = d['select'] and not (d['distance'] > 20 and d['area'] < 50)
    d['select'] = d['select'] and not (d['angle'] > 85 and d['angle'] < 95 and d['len_major'] > 90)
    return d

def tag_image(mask_img1, mask_img2, pois, dect_fct, dect_args, search_radius, 
              crit_multiple='distance'):
    # main loop
    for poi in pois:
        steps = Detector.detect(mask_img1.img, poi, search_radius, dect_fct, 
                                dect_args, plot=False)
        contours, hierarchy = cv.findContours(steps[-1], cv.RETR_TREE, 
                                              cv.CHAIN_APPROX_NONE)
        contours = Detector.unite_family(hierarchy, contours)
        roi, properties, contours = Detector.find_ellipses_in_contours(
            steps[0], contours, draw=False
            )

        for p in properties:
            p = pass_tests(p)

        select = Detector.select_and_sort(zip(properties, contours), 
                                          by='distance')

        try:
            properties = select[0][0]
            contours = select[0][1]
        except IndexError:
            contours = np.empty((0,1,2), dtype=int)
            properties = {}
        
        tags.add("pois", poi)
        tags.add("properties", properties)
        tags.add("tag_contour", contours)
        tags.add("tag_image_orig", steps[0])
        tags.add("tag_image_diff", Detector.get_roi(mask_img2.img, poi, search_radius))

    # wrap up
    tags.move(search_width=search_radius, manual=(0, m0.pars['trim']['t']))
    tags.update_props("xpoi", [px+0 for px, py in tags.pois])
    tags.update_props("ypoi", [py+m0.pars['trim']['t'] for px, py in tags.pois])
    tags.update_props("search_radius", search_radius)
    tags.drop('id')
    tags.drop('select')
    del tags.pois

    return tags


path = "../data/pics/"
copy_to = "../data/annotations/"
date = "20210204"
n = "10"
rad = 50

# load images
img1 = Image(os.path.join(path, date, n, "091544"))
img2 = Image(os.path.join(path, date, n, "091548"))

# mask images
m0 = Slice(img2.img)
m1 = Slice(img1.img)
m0.create_masks(pars="../settings/masking_20210225.json")
m1.create_masks(pars="../settings/masking_20210225.json")

# determin points of interest
pois = Detector.find_pois(
    m0.img, m1.img, filter_fun=filter_contours, 
    threshold=20, sw=20, erode_n=3)

# initialize tagger
tags = Tagger()
dect_args = {'blur':5, 'thresh':10}
tag_image(m0, m1, pois, median_threshold, dect_args, 50)


# export
a = Annotations(img1, 'moving_edge', tag_db_path="")
a.read_new_tags(pd.DataFrame(tags.__dict__))
Files.copy_files(os.path.join(path, date, n), os.path.join(copy_to, date, n), ex1='.tiff', ex2="PNAN")
