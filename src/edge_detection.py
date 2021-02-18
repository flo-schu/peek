# ======= motion analysis to build a database for object detection ============
# this would be a task for a hyperparameter optimization ()

import pandas as pd
from image.process import Series, Image
from image.analysis import Annotations
from evaluation.plot import Viz as viz
import evaluation.calc as calc
from utils.manage import Files
from matplotlib import pyplot as plt
import os
import numpy as np
import cv2 as cv

# mask from top till detection signal
def mask_from_top(mask):
    d = np.flipud(np.flipud(mask).cumsum(axis=0))
    masktop = np.where(d > 0, 0, 255).astype('uint8')

    return masktop

def mask_from_bottom(mask):
    d = np.flipud(np.flipud(mask).cumsum(axis=0))
    masktop = np.where(d > 0, 0, 255).astype('uint8')

    return masktop

def min_filter(n, img):
    size = (n, n)
    shape = cv.MORPH_RECT
    kernel = cv.getStructuringElement(shape, size)

    # Applies the minimum filter with kernel NxN
    return cv.erode(img, kernel)

def max_filter(n, img):
    size = (n, n)
    shape = cv.MORPH_RECT
    kernel = cv.getStructuringElement(shape, size)

    return cv.dilate(img, kernel)


path = "../data/pics/"
date = "20210204"
copy_to = "../data/annotations/"
stop_after=100

s = Series(os.path.join(path, date, "6"))

img = Image(os.path.join(path, date, "8", "091155"))

# 1. trim image roughly
i = img.img[1000:4500,:,:]

# 2. apply mask till blue band is detected
blue_low = np.array([0,30,70])
blue_high = np.array([40,80,140])

mask = cv.inRange(i, blue_low, blue_high)
masktop = mask_from_top(mask)
r = cv.bitwise_and(i, i, mask=masktop)

plt.imshow(r)


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


imin = min_filter(30, r)
plt.imshow(imin)

mask = cv.inRange(imin[:,:,0], 20, 255) # red mask
mask = max_filter(10, mask)

from scipy.ndimage import gaussian_filter1d
from scipy.signal import argrelextrema

start_sediment = []
newmask = np.ones(imin[:,:,0].shape)
for i in range(mask.shape[1]):
    y = mask[2000:,i]
    ys = gaussian_filter1d(y, 10)
    yg = np.gradient(np.gradient(ys))
    try:
        yex = argrelextrema(yg, np.greater)[0][0]
    except IndexError:
        yex = mask.shape[0]
    start_sediment.append(yex)
    newmask[2000+yex:,i] = 0

plt.imshow(newmask)

r2 = cv.bitwise_and(r, r, mask=newmask.astype('uint8'))
plt.imshow(r2)

# also promising:
i = img.img[1000:4500,:,:]
imin = min_filter(30, i)
mask = cv.inRange(imin, np.array([0,0,0]), np.array([10,10,10]))
plt.imshow(mask)




plt.imshow(mask)

ax = plt.subplot()
ax.imshow(mask[2000:,:])
ax.plot(np.array(start_sediment))

plt.plot(yg)
plt.plot(y)
plt.plot(ys)
plt.vlines(yex, ymin=0, ymax=255, color="black")

# for local maxima
argrelextrema(ys, np.greater)

# for local minima
argrelextrema(ys, np.less)

plt.imshow(mask)

r2 = cv.bitwise_and(r, r, mask=mask)
plt.imshow(r2)

mask = cv.inRange(imin[:,:,2], 0, 10) # blue mask
plt.imshow(mask)
masktop = mask_from_top(mask)
r = cv.bitwise_and(i, i, mask=masktop)








# 3. analyse color profile at sediment border
sec = i[2300:2800,810:850,:]
viz.color_analysis(sec, channel="b")

# 4. apply minimum filter and check vertical profile of tank
imin = min_filter(30, r[:,500:1000,:])
viz.color_analysis(imin, "r")
viz.color_analysis(imin, "g")
viz.color_analysis(imin, "b")

imax = max_filter(30, r[:,500:1000,:])
viz.color_analysis(imax, "g")

# 5. apply mask until sediment is over
imin = min_filter(30, r)
imax = max_filter(30, r)
# 5a. cut until sediment starts

mask = cv.inRange(imin[:,:,0], 20, 255) # red mask
mask = max_filter(10,mask)

y = mask.sum(axis=1)
ys = calc.smooth(y, 200)

plt.plot(y)
plt.plot(ys)
from scipy.signal import argrelextrema
# for local maxima
argrelextrema(ys, np.greater)

# for local minima
argrelextrema(y, np.less)

plt.imshow(mask)

r2 = cv.bitwise_and(r, r, mask=mask)
plt.imshow(r2)

mask = cv.inRange(imin[:,:,2], 0, 10) # blue mask
plt.imshow(mask)
masktop = mask_from_top(mask)
r = cv.bitwise_and(i, i, mask=masktop)







# ich muss die detection nur oben machen. Denn da sind die unbeweglichen Culex.
# Alles was nicht an der wasseroberfläche ist, bewegt sich. Dann muss ich nur noch die 
# Intersection der oben bewgten und edge detektierten voneinander abziehen.

# step by step. Next Daphnia low has to be increased in order not to caputre 

# so I could take the kernel and look
plt.imshow(r[:,:,0]+r[:,:,1])
plt.imshow(r[:,:,0]*2+r[:,:,1]/(r[:,:,2]+1))

i = r[:,:,0] + r[:,:,1]
# %matplotlib
# i.show()
gray = cv.cvtColor(img.img,cv.COLOR_BGR2GRAY)
plt.imshow(i,cmap="gray")
plt.imshow(gray,cmap="gray")
horiz = cv.Sobel(i, 0, 1, 0, cv.CV_64F, ksize=5)
vert  = cv.Sobel(i, 0, 0, 1, cv.CV_64F, ksize=5)

sob = cv.bitwise_or(horiz,vert)
plt.imshow(sob)
# (T, thresh) = cv.threshold(bitwise_or, 250, 255, cv.THRESH_BINARY)
# plt.imshow(thresh,cmap="gray")
cnts = cv.findContours(sob, cv.RETR_LIST, cv.CHAIN_APPROX_SIMPLE)


cv2.imwrite(path+"1166_thresh.tiff", thresh)

plt.imshow(bitwise_or, cmap="gray")

# corner detection


img = i.img
gray = np.float32(gray)
dst = cv.cornerHarris(gray,10,3,0.04)
#result is dilated for marking the corners, not important
dst = cv.dilate(dst,None)
# Threshold for an optimal value, it may vary depending on the image.
img[dst>0.01*dst.max()]=[255,0,0]
plt.imshow(img)


a = Annotations(i, 'motion_analysis', '../data/tag_db.csv')
a.load_processed_tags()
# %matplotlib
a.start()
a.show_tag_number(0)

# - [ ] Important: Write detector for Culex
# - [ ] what about zero sized images?
# - [ ] Address memory problems when six images were taken from one nanocosm (need 1.2 GB
        # memory)