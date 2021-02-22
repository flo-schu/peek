# ======= motion analysis to build a database for object detection ============
# this would be a task for a hyperparameter optimization ()

import pandas as pd
from image.process import Series, Image
from image.analysis import Annotations
from image.analysis import Spectral as spec
from evaluation.plot import Viz as viz
import evaluation.calc as calc
from utils.manage import Files
from matplotlib import pyplot as plt
import cv2 as cv

import os
import numpy as np


# mask from top till detection signal


path = "../data/pics/"
date = "20210204"
copy_to = "../data/annotations/"
stop_after=100

s = Series(os.path.join(path, date, "7"))

# img = Image(os.path.join(path, date, "8", "091155"))
# img = Image(os.path.join(path, date, "6", "090953"))
img = Image(os.path.join(path, date, "7", "091355"))

# 1. trim image roughly
i = img.img[1000:4500,:,:]

# remove from end of blue band to top ------------------------------------------
# 2. apply mask till blue band is detected
blue_low = np.array([0,20,60])
blue_high = np.array([50,90,150])

# create preliminary mask of blue band
# mask = cv.inRange(i, blue_low, blue_high)
mask = spec.mrm(i, 20, (blue_low, blue_high), 50)
plt.imshow(mask)

masktop = spec.mask_from_top(mask)
r = cv.bitwise_and(i, i, mask=masktop)

plt.imshow(r)

# remove sediment --------------------------------------------------------------
# create prelimary mask of sediment 
gray = cv.cvtColor(r, cv.COLOR_BGR2GRAY)
y_offset = 2000
mask = spec.mrm(gray[2000:], 30, (50, 255), 100)

# detect peaks
left, right = spec.detect_vertical_peaks(mask, height=250, width = 200)

# redraw mask based on peak analysis
# using np.zeros instead of np.ones with fill=1 instead of fill=0 
# inverts the process
newmask = spec.extend_horiz_border(
    left, img=np.ones(gray.shape), towards="bottom", 
    y_offset=(y_offset, y_offset), fill=0)


r2 = cv.bitwise_and(r, r, mask=newmask.astype('uint8'))
plt.imshow(r2)

# remove distance to water surface ---------------------------------------------
y_offset = 1000
mask = spec.mrm(gray[:y_offset], 30, (60, 255), 50)
plt.imshow(mask)
# detect peaks
left, right = spec.detect_vertical_peaks(mask, height=250, width = 50)

newmask = spec.extend_horiz_border(
    right, img=np.ones(gray.shape), towards="top", 
    y_offset=(0, 0), fill=0)
plt.imshow(newmask)

r3 = cv.bitwise_and(r2, r2, mask=newmask.astype('uint8'))
plt.imshow(r3)

# remove water surface ---------------------------------------------------------
y_offset = 1000

# detect peaks
mask = spec.mrm(r3[:y_offset,:,2], 10, (5, 255), 50)
left, right = spec.detect_vertical_extrema(mask, smooth_n=10, derivative=1)
newmask = spec.extend_horiz_border(
    left, img=np.zeros(gray.shape), towards=right, 
    y_offset=(0, 0), fill=1, smooth_n=10)

r4 = cv.bitwise_and(r3, r3, mask=newmask.astype('uint8'))
plt.imshow(r4)


# can the problems be resolved by fitting a cubic function through the points?
# because normally the correct points are identified


# plt.plot(gaussian_filter1d(right,100)); plt.plot(gaussian_filter1d(left,100))
# len(left)



# 3. apply mask until sediment is over
# minimum filters are used for this, because when the 
# radius is big enough, floating objects in water are "overwritten" with
# background. since sediment is continuously coloured, minimum of color 
# ranges is much higher here.

# to detect the sediment border, the picture is split in half, because in the
# lower half the sediment will start eventually.
# the input is a minimum filter of input image, from which a mask is calculated
# from the red channel because it has a very distinct transition from background 
# to sediment. Then a max filter is calculated from this to make the sediment 
# more homogeneous
# [ ] this could be improved by including other color channels as well
# [ ] or converting to greyscale beforehand

# Next, vertical 1D slices are passed to np.gradient two times to get
# the locations of the inflection points. The first one, marks the transition to 
# the sediment. 
# [ ] Maybe this could again be improved by finding the closest inflection
#     point to the previous, thus noisy (up and down moevements would be avoided)
#     !!!
# From the resulting line, a mask is extended until the bottom and contains the
# sediment.
# The good thing with this, is that we are only slightly dependent on a color range 
# because this changes with lighting conditions or sediment cover, the important
# thing necessary is a big enough change. 

# next time try out:
# 1. Greyscale
# 2. min filter --> mask --> max filter
# 3. detect change
# 4. find beginning and then advance by closest location

