# author: Florian Schunck
# date: 14.11.2020
#
# Descritption:
# Class for image analysis of nanocosm image files (RAW)
# containing methods for cropping, difference of continuous images, edge detection

import os
import rawpy
import imageio
import cv2
from pyzbar import pyzbar
import matplotlib.pyplot as plt
import numpy as np

class Image:
    def __init__(self, path):
        assert os.path.exists(path), print("path does not exist, working directory:", os.getcwd())
        self.path = path
        self.img = None
        self.raw = None
        self.meta = None
        self.edited = None
        self.diff = None
        self.id = 0

    def read_raw(self, **params):
        with rawpy.imread(self.path) as raw:
             self.raw = raw.postprocess(**params)

        self.img = self.raw

    def save(self, what, file_ext="tiff", delete_old=False):
        what = getattr(self, what)
        imageio.imwrite(os.path.splitext(self.path)[0]+"."+file_ext, what)
        
    def remove_original(self):
        os.remove(self.path)

    def restore_original(self):
        self.img = self.raw

    def crop_tb(self, reduce_top, reduce_bottom):
        self.img = self.img[reduce_top:reduce_bottom, :,:]
        
    def crop_black_lr(self):
        # calculate sum of rgb colors (black is zero) and take minimum along columns
        temp = self.img.sum(axis=2).min(axis=0)

        # take cumulative sum of BW values in each column
        # to find the longest continuous row of black.
        # This is where is to be cut off
        cutl = temp.cumsum() != 0
        cutr = temp[::-1].cumsum()[::-1] != 0

        # take subset of cuts from left and right
        self.img = self.img[:, np.logical_and(cutl,cutr),:]

    def read_qr_code(self):
        # improve image 
        contrast = cv2.addWeighted( self.img, 2, self.img, 0, 0)
        gray = cv2.cvtColor(contrast,cv2.COLOR_BGR2GRAY)
        # plt.imshow(gray, cmap='gray'), plt.axis("off")
        blur = cv2.GaussianBlur(gray, (9,9), 0)
        # plt.imshow(blur, cmap='gray'), plt.axis("off")
        thresh = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        # plt.imshow(thresh, cmap='gray'), plt.axis("off")
        
        # read QR Code & convert to string
        try:
            code = pyzbar.decode(thresh)[0]
            message = code.data.decode("utf-8")
            parts = message.split(sep="_")
            self.id = parts[1]
        except IndexError:        
            self.id = 999
        
class Series(Image):
    def __init__(self, directory="", image_list=[]):
        self.dirpath = directory
        self.image_list = image_list
        self.images = []
        self.diffs = None

    def read_images(self, **params):
        if len(self.image_list) == 0:
            files = os.listdir(self.dirpath)
        else:
            files = self.image_list

        images = []
        for f in files:
            i = Image(path=os.path.join(self.dirpath,f))
            i.read_raw(**params)
            print("processed file: {}".format(f))
            i.read_qr_code()
            print("read QR code: {}".format(i.id))
            images.append(i)

        self.images = images

    def difference(self):
        """
        calculates the RGB differences between every two consecutive images.
        The last difference is the diff between last and first image
        """
        # changing the dtype from uint to int is very important, because
        # uint does not allow values smaller 0
        ims = np.array([i.img for i in self.images], dtype=int)
        diffs = np.diff(np.concatenate((ims,ims[0:,:,:,:]), axis=0), axis=0)
        
        for i, d in zip(self.images, np.arange(len(self.images))):
            i.diff = diffs[d]

    def save(self, what):
        for i in self.images:
            i.save(what)


# a = Image(path = "../../data/pics/20201112/Serienbilder013/P1000086.RW2")
# a.read_raw()
# a.save()
# a.crop_tb(1000,4000)
# a.crop_black_lr()
# a.save('img')

# s = Series("../../data/pics/20201112/Serienbilder013/")
# s.read_images()
# s.difference()
# s.save('diff')
