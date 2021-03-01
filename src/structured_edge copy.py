import cv2
import os
import numpy as np

from image.process import Series, Image
from image.analysis import Mask, Spectral
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
        self.mask_airspace(**self.pars['airspace'])        
        self.mask_water_surface(**self.pars['water_surface'])


masks = Slice(img.img)
masks.create_masks(pars="../settings/masking_20210225.json")

mdiff = Slice(img2.img)
mdiff.create_masks(pars="../settings/masking_20210225.json")

diff = Series.difference([masks.img, mdiff.img], lag=1, smooth=5)
plt.imshow(img2.img)
plt.imshow(diff[1])

image = mdiff.img.astype(np.float32) / 255.0

# initialize the structured edge detector with the model
edge_detector = cv2.ximgproc.createStructuredEdgeDetection('../data/dnn/model.yml')
# detect the edges
edges = edge_detector.detectEdges(image)
edges2 = (edges * 255).astype('uint8')
plt.imshow(edges2)

# thresholding helps a lot for the contours (for now)
ret,thresh = cv2.threshold(edges2,10,255,0)
plt.imshow(thresh)

# extract contours
contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
len(contours)

# more work needs to be done on contours
# c = contours[500]
# contours[0]
ellipses = []
bboxes = []
img = image
for i, c in enumerate(contours):
    nc = contours[hierarchy[0][i, 1]]
    if cv2.moments(c)['m01']-cv2.moments(nc)['m01'] > 10:
        if cv2.contourArea(c) > 10:
            e = cv2.fitEllipse(c)
            ellipses.append(e)
        else:
            b = cv2.boundingRect(c)
            bboxes.append(b)

    # if hierarchy[0][i, 2] == -1:
    #     img = cv2.ellipse(img,e,(0,255,0),2)
    # if hierarchy[0][i, 2] > 0:
        img = cv2.ellipse(img,e,(255,0,0),1)

# get with structuring element. I like
k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, ksize=(20,20))
morph = cv2.morphologyEx(thresh, op=cv2.MORPH_CLOSE, kernel=k)
plt.imshow(morph)
contours, hierarchy = cv2.findContours(morph, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
len(contours)
img = image.copy()

for c in contours:
    if cv2.moments(c)['m00'] > 10000:
        pass
    elif cv2.moments(c)['m00'] < 15:
        pass
    else:
        e = cv2.fitEllipse(c)
        img = cv2.ellipse(img,e,(255,255,0),2)
        # cv2.drawContours(img, [c],0, color=(0,255,0), thickness=2)

fig, (ax1, ax2) = plt.subplots(1,2, sharey=True, sharex=True)

ax1.imshow(img)
ax2.imshow(diff[0])
len(ellipses)

plt.imshow(img)
cv2.isContourConvex(c)




