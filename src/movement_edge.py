import cv2 as cv
import os
import numpy as np
import itertools as it

from image.process import Series, Image, Tags
from image.analysis import Mask, Spectral, Detector
from evaluation.plot import Viz
from utils.manage import Files
from matplotlib import pyplot as plt

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

def smart(roi):
    median = cv.medianBlur(roi, 5)
    background = Detector.substract_median(median, ignore_value=0)
    gray = cv.cvtColor(background, cv.COLOR_RGB2GRAY)
    T, thresh = cv.threshold(gray, 10, 255, 0)

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



path = "../data/pics/"
date = "20210204"

s = Series(os.path.join(path, date, "7"))

# img = Image(os.path.join(path, date, "8", "091155"))
# img = Image(os.path.join(path, date, "7", "091355"))
# img = Image(os.path.join(path, date, "6", "090953"))
# img = Image(os.path.join(path, date, "12", "091920"))
img1 = Image(os.path.join(path, date, "10", "091544"))
img2 = Image(os.path.join(path, date, "10", "091546"))
img2 = Image(os.path.join(path, date, "10", "091548"))
# img1 = Image(os.path.join(path, date, "11", "091732"))
# img2 = Image(os.path.join(path, date, "11", "091734"))

m0 = Slice(img2.img)
m1 = Slice(img1.img)
m0.create_masks(pars="../settings/masking_20210225.json")
m1.create_masks(pars="../settings/masking_20210225.json")

pois = Detector.find_pois(
    m0.img, m1.img, filter_fun=filter_contours, 
    threshold=20, sw=20, erode_n=3)

tags = Tags()
rad = 50

for ip, poi in enumerate(pois):
    
    tags.add("pois", poi)
    steps = Detector.detect(m1.img, poi, rad, smart, {}, plot=False)
    contours, hierarchy = cv.findContours(steps[-1], cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    contours = Detector.unite_family(hierarchy, contours)
    roi, properties, contours = Detector.find_ellipses_in_contours(steps[0], contours, draw=False)

    for p in properties:
        p = pass_tests(p)

    c_select = [(p['distance'], p['id']) for p in properties if p['select']]
    
    try:
        c_select = [i for _, i in sorted(c_select)][0]
        roi, properties, contours = Detector.find_ellipses_in_contours(steps[0], [contours[c_select]], draw=True)
        tags.add("tag_contour", contours[0])
        tags.add("tag_image_orig", roi)
        tags.add("tag_image_diff", Detector.get_roi(m0.img, poi, rad))
        tags.add("properties", properties[0])

    except IndexError:
        tags.set_none(["tag_contour", "tag_image_orig", "tag_image_diff", "properties"])        

    print(ip)


tags.move()


# plt.imshow(steps[0])
# new_tags = {
#     'tag_contour': cnts_select,
#     'tag_image_orig': imslc1,
#     'tag_image_diff': imslc2,
# }


# steps:
# 1. run analysis for whole image.
# 2. Integrate into Annotations framework
#    --> passing lists to img.    



