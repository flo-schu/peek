# ======= motion analysis to build a database for object detection ============
# this would be a task for a hyperparameter optimization ()

import pandas as pd
from image.process import Series, Image
from image.analysis import Annotations
from utils.manage import Files
from matplotlib import pyplot as plt
import os
import numpy as np
import cv2 as cv
 
path = "../data/pics/"
date = "20210204"
copy_to = "../data/annotations/"
stop_after=100

s = Series(os.path.join(path, date, "6"))

img = Image(os.path.join(path, date, "6", "090951"))

# 1. steps cut out only water

i = img.img[1000:4500,:,:]

blue_low = np.array([0,30,70])
blue_high = np.array([40,80,140])
mask = cv.inRange(i, blue_low, blue_high)

d = np.flipud(np.flipud(mask).cumsum(axis=0))
mask2 = np.where(d>0,0, 255).astype('uint8')

r = cv.bitwise_and(i, i, mask=mask2)
plt.imshow(r)

blue_low = np.array([0,30,70])
blue_high = np.array([40,80,140])
mask = cv.inRange(i, blue_low, blue_high)

# im pretty sure this can be well done with color ranges!

plt.imshow(r)
lines=plt.plot(i[2300:2800,810:850,1])

# check out channel 1 The dwo peaks are daphnia, afterwards comes the sediment
# there is already a difference

# in channel 0 this is pretty much the same. 
lines=plt.plot(i[2300:2800,810:850,0])

# Addition of channel 0 and 1 should bring out a nice difference
lines=plt.plot(i[2300:2800,810:850,1].max(axis=1))
# here I can identidy a decision boundary between sediment and water. 

lines=plt.plot(i[2300:2800,810:850,2].max(axis=1))

daphnia_low = np.array([50,40,10])
daphnia_high = np.array([80,70,40])
mask = cv.inRange(r, daphnia_low, daphnia_high)
plt.imshow(mask)

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
%matplotlib
a.start()
a.show_tag_number(0)

# - [ ] Important: Write detector for Culex
# - [ ] what about zero sized images?
# - [ ] Address memory problems when six images were taken from one nanocosm (need 1.2 GB
        # memory)