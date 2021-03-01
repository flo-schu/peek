import cv2 as cv
import os
import numpy as np
import itertools as it

from image.process import Series, Image
from image.analysis import Mask, Spectral, Detection
from evaluation.plot import Viz
from utils.manage import Files
from matplotlib import pyplot as plt

path = "../data/pics/"
date = "20210204"

s = Series(os.path.join(path, date, "7"))

# img = Image(os.path.join(path, date, "8", "091155"))
# img = Image(os.path.join(path, date, "7", "091355"))
# img = Image(os.path.join(path, date, "6", "090953"))
# img = Image(os.path.join(path, date, "12", "091920"))
img1 = Image(os.path.join(path, date, "10", "091544"))
img2 = Image(os.path.join(path, date, "10", "091546"))
img1 = Image(os.path.join(path, date, "11", "091732"))
img2 = Image(os.path.join(path, date, "11", "091734"))



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
       

m0 = Slice(img2.img)
m1 = Slice(img1.img)
m0.create_masks(pars="../settings/masking_20210225.json")
m1.create_masks(pars="../settings/masking_20210225.json")

pois = Detection.find_pois(
    m0.img, m1.img, filter_fun=filter_contours, 
    threshold=20, sw=20, erode_n=3)

def smart(roi):
    median = cv.medianBlur(roi, 5)
    background = median.astype('int')
    background[:,:,2] = median[:,:,2] - np.median(median[:,:,2].flatten())
    background[:,:,1] = median[:,:,1] - np.median(median[:,:,1].flatten())
    background[:,:,0] = median[:,:,0] - np.median(median[:,:,0].flatten())
    background = np.where(background > 0, background, 0).astype('uint8')
    gray = cv.cvtColor(background, cv.COLOR_BGR2GRAY)
    
    T, thresh = cv.threshold(gray, 10, 255, 0)

    return [roi, median, background, gray, thresh]

steps = Detection.detect(
    m1.img, pois[198], 50, 
    smart, {}, 
    plot=True)


# steps:
# 1: take contours
# 2: select one contour which is:
#    - is not very small
#    - is not a near, horizontal line of length of the search window (water surface)
#    - closest to the center
#    - and one of the largest
    



