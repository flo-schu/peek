# ======= motion analysis to build a database for object detection ============
# this would be a task for a hyperparameter optimization ()

import os
import cv2 as cv
import numpy as np
from image.process import Series, Image
from image.analysis import Mask
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
img = Image(os.path.join(path, date, "11", "091732"))

# here I can create my own individual program of functions, that I want to execute
# This is very nice, because here it makes it explicit what is to be done,
# but leaves the overhead out of the way
class Slice(Mask):
    def create_masks(self, pars):
        super().create_masks(pars)

        self.img = self.trim(self.img, **self.pars['trim'])
        self.remove_blue_tape(**self.pars['blue_tape'])
        self.mask_sediment(**self.pars['sediment'])     
        self.mask_airspace(**self.pars['airspace'])        
        self.mask_water_surface(**self.pars['water_surface'])


masks = Slice(img.img)
masks.create_masks(pars="../settings/masking_20210225.json")
plt.imshow(masks.img)



i = masks.img
i2 = i[:,:,0] + i[:,:,1] - i[:,:,2]
gray = cv.cvtColor(masks.img,cv.COLOR_BGR2GRAY)
# imin = Slice.min_filter(5, i)
edges = cv.Canny(i, 100, 170, apertureSize=3, L2gradient=None)

plt.imshow(edges)
cnts = Series.get_contours(edges, threshold=5)
len(cnts)
plt.imshow(Image.tag_image(masks.img, cnts))

# %matplotlib
# i.show()
plt.imshow(i2,cmap="gray")
plt.imshow(i,cmap="gray")
plt.imshow(gray,cmap="gray") 
imin = Slice.min_filter(5, i)
horiz = cv.Sobel(imin, 0, 1, 0, cv.CV_64F, ksize=5)
vert  = cv.Sobel(imin, 0, 0, 1, cv.CV_64F, ksize=5)

sob = cv.bitwise_or(horiz,vert)
plt.imshow(sob, cmap="gray")
gray = cv.cvtColor(sob,cv.COLOR_BGR2GRAY)
plt.imshow(gray,cmap="gray")
imin = Slice.min_filter(3, sob)
plt.imshow(imin)
gray = imin[:,:,0].astype('int')*imin[:,:,1].astype('int')
gray = gray / gray.max() * 255
gray = gray.astype('uint8')
plt.imshow(gray)
(T, thresh) = cv.threshold(gray, 150, 255, cv.THRESH_BINARY)
plt.imshow(thresh)
imin = Slice.min_filter(2, thresh)
imax = Slice.max_filter(3, imin)
plt.imshow(imax)
len(cnts)



plt.imshow(dst)

low = np.array([50,50,0])
high = np.array([200,200,10])

test = cv.inRange(sob, low, high)

plt.imshow(test)

Viz.color_analysis(sob[600:800, 1240:1260], "r")

plt.imshow(sob3)

plt.imshow(sob2, cmap="gray")
# plt.imshow(thresh,cmap="gray")


cv2.imwrite(path+"1166_thresh.tiff", thresh)

plt.imshow(bitwise_or, cmap="gray")

# corner detection

dst = cv.cornerHarris(gray,10,7,0.04)

img = i.img
gray = np.float32(gray)
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