# ======= motion analysis to build a database for object detection ============
# this would be a task for a hyperparameter optimization ()

import pandas as pd
from image.process import Series, Image
from image.analysis import Annotations
from evaluation.plot import Viz as viz
import evaluation.calc as calc
from utils.manage import Files
from matplotlib import pyplot as plt

from scipy.ndimage import gaussian_filter1d
from scipy.signal import argrelextrema, find_peaks

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

def mrm(img, min_kernel_n, range_threshold, max_kernel_n):
    """
    mrm - minimum filter followed by a range threshold and followed by a 
    maximum filter. Is a sequence of image processing steps creates a mask.
    This mask filters a bright and relatively homogeneous feature of an image 
    which has a strong contrast to the surrounding.

    xxx_kernel_n    stands for the kernel size of the respective minimum or 
                    maximum functions. The kernel takes the minimum or maximum
                    respectively for the N x N sized matrix of the kernel
    
    range_threshold transforms the continuous image to a mask consisting of 
                    0 or 255 values. Takes a tuple like object and needs a 
                    min and max threshold like: (20, 255). See cv.inRange()
    """
    img = min_filter(min_kernel_n, img)
    mask = cv.inRange(img, range_threshold[0], range_threshold[1]) # red mask
    mask = max_filter(max_kernel_n, mask)

    return mask


def detect_vertical_peaks(img, return_prop="ips", **peak_args):
    """
    Goes through an image by vertical slices and returns the first peak
    encountered. Peak arguments can pe provided by keywords. Refer to
    scipy.signal find_peaks method to know what arguments can be used. 
    Well working are height and width. Particularly the width argument is 
    important to ensure that only strong enough signals are detected.
    """
    y, x = img.shape
    
    left = [0]
    right = [y]
    
    for i in range(x):
        vline = img[:,i]
        peak_x, props = find_peaks(vline, **peak_args)
        try:
            if len(peak_x) > 1:
                print(i, "more than one peak")
            left.append(props['left_'+return_prop][0])
            right.append(props['right_'+return_prop][0])
        except IndexError:
            left.append(left[i-1])
            right.append(right[i-1])

    return left[1:], right[1:]

def detect_vertical_extrema(img, smooth_n=10, derivative=1):
    """
    finds extrema in spectral vertical lines of an image. At the moment optimized for
    first derivative. 
    Basically the function looks for an increase first and takes the beginning of 
    the increase and then looks for the decrease of a value again.
    Since the water surface behaves in pretty much this fashion, it works ok
    Wait for problematic images

    Interpolation could help a lot in these cases.
    """
    y, x = img.shape
    
    left = [0]
    right = [y]

    for i in range(x):
        vline = img[:,i]
        if smooth_n > 0:
            vline = gaussian_filter1d(vline, smooth_n)
        
        vline = np.gradient(vline, derivative)
        ex1 = argrelextrema(vline, np.less)[0]
        ex2 = argrelextrema(vline, np.greater)[0]
        try:
            left.append(ex1[0])
        except IndexError:
            print("not enough peaks.")
            left.append(left[i-1])

        try:
            right.append(ex2[1])
        except IndexError:
            print("not enough peaks.")
            right.append(right[i-1])


    return left[1:], right[1:]

def extend_horiz_border(border, img, towards="bottom", smooth_n=0, 
                        y_offset=(0,0), fill=0):
    
    """
    The method takes a 1D array or list as an input as well as an image. Both
    must have the same x dimension (eg. if the border is of len 10, the image 
    must by Y x 10 as well. It returns an image which is filled from the 
    border until top or bottom or until a second border). 
    
    border      1D array of same x-dimension as img
    img         2D array
    smooth_n    if set to value greater 1, the array is smoothed beforehand
    y_offset    array like of len=2, specifies if the border is offset and the
                second interval is offset as well
    fill        is the number with whihc the array is filled
    """
    y, x = img.shape
    
    if smooth_n > 0:
        a = np.round(gaussian_filter1d(border, smooth_n)).astype('int')
    else:
        a = np.round(border).astype('int')

    a = a + y_offset[0]
    
    assert len(a) == x, "img and border should have the same x dimension"
    
    if isinstance(towards, (np.ndarray, list)):
        if smooth_n > 0:
            b = np.round(gaussian_filter1d(towards, smooth_n)).astype('int')
        else:
            b = np.round(towards).astype('int')
        
        b = b + y_offset[1]
        assert len(a) == len(b)
    elif towards == "bottom":
        b = np.repeat(y+y_offset[1], x)
    elif towards == "top":
        b = a
        a = np.repeat(0+y_offset[1], x)


    # im sure for this exists a numpy method        
    for i in range(x):
        img[a[i]:b[i], i] = fill

    return img

path = "../data/pics/"
date = "20210204"
copy_to = "../data/annotations/"
stop_after=100

s = Series(os.path.join(path, date, "6"))

img = Image(os.path.join(path, date, "8", "091155"))

# 1. trim image roughly
i = img.img[1000:4500,:,:]

# remove from end of blue band to top ------------------------------------------
# 2. apply mask till blue band is detected
blue_low = np.array([0,20,60])
blue_high = np.array([50,90,150])

# create preliminary mask of blue band
# mask = cv.inRange(i, blue_low, blue_high)
mask = mrm(i, 20, (blue_low, blue_high), 50)
plt.imshow(mask)

masktop = mask_from_top(mask)
r = cv.bitwise_and(i, i, mask=masktop)

plt.imshow(r)

# remove sediment --------------------------------------------------------------
# create prelimary mask of sediment 
gray = cv.cvtColor(r, cv.COLOR_BGR2GRAY)
y_offset = 2000
mask = mrm(gray[2000:], 30, (50, 255), 100)

# detect peaks
left, right = detect_vertical_peaks(mask, height=250, width = 200)

# redraw mask based on peak analysis
# using np.zeros instead of np.ones with fill=1 instead of fill=0 
# inverts the process
newmask = extend_horiz_border(
    left, img=np.ones(gray.shape), towards="bottom", 
    y_offset=(y_offset, y_offset), fill=0)


r2 = cv.bitwise_and(r, r, mask=newmask.astype('uint8'))
plt.imshow(r2)

# remove distance to water surface ---------------------------------------------
y_offset = 1000
mask = mrm(gray[:y_offset], 30, (60, 255), 50)
plt.imshow(mask)
# detect peaks
left, right = detect_vertical_peaks(mask, height=250, width = 50)

newmask = extend_horiz_border(
    right, img=np.ones(gray.shape), towards="top", 
    y_offset=(0, 0), fill=0)
plt.imshow(newmask)

r3 = cv.bitwise_and(r2, r2, mask=newmask.astype('uint8'))
plt.imshow(r3)

# remove water surface ---------------------------------------------------------
y_offset = 1000

viz.color_analysis(r3[0:1000,200:400,:], "b")


plt.imshow(r3[:y_offset,:,2])
# detect peaks
mask = mrm(r3[:y_offset,:,2], 10, (10, 255), 50)
plt.imshow(mask)
left, right = detect_vertical_extrema(mask, smooth_n=10, derivative=1)
newmask = extend_horiz_border(
    left, img=np.zeros(gray.shape), towards=right, 
    y_offset=(0, 0), fill=1, smooth_n=10)
plt.imshow(newmask)

r4 = cv.bitwise_and(r3, r3, mask=newmask.astype('uint8'))
plt.imshow(r4)


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






plt.plot(b)
plt.plot(start_sediment)

plt.imshow(mask)


plt.imshow(r)

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