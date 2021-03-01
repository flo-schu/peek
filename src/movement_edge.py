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
# img = Image(os.path.join(path, date, "10", "091544"))
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
       
def structured_edge(roi, detector=None, thresh=0.06, morph_kernel=20):
    edges = detector.detectEdges(roi.astype(np.float32) / 255.0)
    ret, thresh = cv.threshold(edges,thresh,1,0)
    morph = cv.morphologyEx(thresh, op=cv.MORPH_CLOSE, kernel=morph_kernel)
    return [roi, edges, thresh, morph]


m0 = Slice(img2.img)
m1 = Slice(img1.img)
m0.create_masks(pars="../settings/masking_20210225.json")
m1.create_masks(pars="../settings/masking_20210225.json")

i = 34
bw = 50
edge_detector = cv.ximgproc.createStructuredEdgeDetection('../data/dnn/model.yml')

k = cv.getStructuringElement(cv.MORPH_ELLIPSE, ksize=(40,40))
pois = Detection.find_pois(
    m0.img, m1.img, filter_fun=filter_contours, 
    threshold=20, sw=20, erode_n=3)


def crange(roi, smooth=3, morph_kernel=None):
    mini = Spectral.min_filter(9, roi)
    gray = cv.cvtColor(mini, cv.COLOR_RGB2GRAY)
    smooth = cv.filter2D(gray, ddepth=-1, kernel=np.ones((smooth,smooth))/smooth**2)
    horiz = cv.Sobel(smooth, 0, 1, 0, cv.CV_64F, ksize=5)
    vert  = cv.Sobel(smooth, 0, 0, 1, cv.CV_64F, ksize=5)
    sob = cv.bitwise_or(horiz,vert)
    T, thresh = cv.threshold(sob, 50, 255, 0)
    morph = cv.morphologyEx(thresh, op=cv.MORPH_CLOSE, kernel=morph_kernel)
    return [roi, mini, gray, smooth, thresh, morph]


def analytic(roi, detector):
    edges = detector.detectEdges(roi.astype(np.float32) / 255.0)
    ret, thresh = cv.threshold(edges.astype('uint8'),30,255,0)
    print(thresh)
    contours, h = cv.findContours(thresh, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    img = roi.copy()
    for i, c in enumerate(contours):
        if cv.contourArea(c) > 10:
            e = cv.fitEllipse(c)

            img = cv.ellipse(img,e,(255,0,0),1)

    return [roi, edges, thresh, img]

def sobel(roi, smooth):
    # mini = Spectral.min_filter(13, roi)
    smooth = cv.filter2D(roi, ddepth=-1, kernel=np.ones((smooth,smooth))/smooth**2)
    col = smooth[:,:,0] - smooth[:,:,2]
    maxi = Spectral.max_filter(10, col)
    horiz = cv.Sobel(maxi, 0, 1, 0, cv.CV_64F, ksize=5)
    vert  = cv.Sobel(maxi, 0, 0, 1, cv.CV_64F, ksize=5)
    sob = cv.bitwise_or(horiz,vert)
    T, thresh = cv.threshold(sob, 80, 255, 0)

    return [roi, smooth, col, maxi, sob]

def canny(roi, smooth):
    # mini = Spectral.min_filter(13, roi)
    # mini = Spectral.min_filter(5, roi)
    smooth = cv.filter2D(roi, ddepth=-1, kernel=np.ones((smooth,smooth))/smooth**2)
    col = smooth[:,:,0] - smooth[:,:,2]
    maxi = Spectral.max_filter(5, col)

    canny = cv.Canny(maxi, 20, 40)

    contours, h = cv.findContours(canny, cv.RETR_TREE, cv.CHAIN_APPROX_NONE)
    img = roi.copy()
    for i, c in enumerate(contours):
        e = cv.fitEllipse(c)

        img = cv.ellipse(img,e,(255,0,0),1)

    return [roi, smooth, col, maxi, canny, img]

crange_args = {'smooth':7, 'morph_kernel':k}
se_args = {'detector': edge_detector, 'thresh': 0.03, 'morph_kernel': k}
ana_args = {'detector': edge_detector}
sobel_args = {'smooth':5}



steps = Detection.detect(
    m1.img, pois[30], 50, 
    structured_edge, se_args, 
    plot=True)








