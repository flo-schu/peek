import cv2
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

image = masks.img.astype(np.float32) / 255.0

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


c = contours[1]
img = cv2.drawContours(image, contours, 500, (255,0,0),3)
plt.imshow(image)

# more work needs to be done on contours
cv2.isContourConvex(c)

plt.imshow(edges)
plt.imshow(canny)