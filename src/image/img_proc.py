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
import imutils

class Image:
    def __init__(self, path):
        assert os.path.exists(path), print("path does not exist, working directory:", os.getcwd())
        self.path = path
        self.img = None
        self.raw = None
        self.meta = None
        self.edited = None
        self.id = 0


    def read_raw(self, **params):
        """
        reads raw file using rawpy module. 
        A future version could use pillow (PIL), because of the possibility to
        read metadata better. However, RW2 files are currently not supported. 
        It is possible though to write a custom image plugin which recognizes the
        raw file.
        https://pillow.readthedocs.io/en/stable/handbook/writing-your-own-file-decoder.html
        """
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
            self.id = int(parts[1])
        except IndexError:        
            self.id = 999
        
class Series(Image):
    def __init__(self, directory="", image_list=[]):
        self.dirpath = directory
        self.image_list = image_list
        self.images = []


    def read_images(self, **params):
        if len(self.image_list) == 0:
            files = os.listdir(self.dirpath)
            files = [i  for i in files if i.split(".")[1] == "RW2"]
            print(files)
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

    def difference(self, lag, smooth):
        """
        calculates the RGB differences between every two consecutive images.
        The last difference is the diff between last and first image
        """
        # changing the dtype from uint to int is very important, because
        # uint does not allow values smaller 0
        imlist = self.images.copy()
        # imlist.append(self.images[0])
        kernel = np.ones((smooth,smooth),np.float32)/smooth**2
        ims = np.array([cv2.filter2D(i.img,-1,kernel) for i in imlist], dtype=int)
        # ims = np.array([i.img for i in imlist], dtype=int)
        diff = np.diff(ims, n=lag, axis=0)
        diffs = np.where(diff >= 0, diff, 0)

        return [diffs[i,:,:,:].astype('uint8') for i in range(len(diffs))]        

    def save(self, what):
        for i in self.images:
            i.save(what)

    def save_list(self, imlist, name='image', file_ext='tiff'):
        for i in range(len(imlist)):
            imageio.imwrite(self.dirpath+name+"_"+str(i)+"."+file_ext, imlist[i])


    def motion_analysis(self, lag=1, thresh_binary=15, thresh_size=10, mar=10, smooth=1):
        """
        motion analysis algorithm. First computes the difference between images.
        
        lag:            is the step between images which are differenced. Default is 1.
                        the higher the step the more pronounced the images should be. 
                        but consequently fewer images are available
        thresh_binary:  threshold to create a binary image from a gray image
        thresh_size:    after tag boxes have been drawn, choose select boxes
                        with maximum extension (x or y) of 'thresh_size'
        """
        diffs = self.difference(lag, smooth)
        contours = []
        tagged_ims = []

        for i in range(len(diffs)):
            orig = self.images[ lag + i ].img

            gray = cv2.cvtColor(diffs[i], cv2.COLOR_BGR2GRAY)

            #threshold the gray image to binarise it. Anything pixel that has
            #value more than 3 we are converting to white
            #(remember 0 is black and 255 is absolute white)
            #the image is called binarised as any value less than 3 will be 0 and
            # all values equal to and more than 3 will be 255
            (T, thresh) = cv2.threshold(gray, thresh_binary, 255, cv2.THRESH_BINARY)

            cnts = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)

            cnts_select = []
            for c in cnts:
                # fit a bounding box to the contour
                if max(c.shape) > thresh_size:            
                    cnts_select.append(c)
               
            imtag = self.tag_image(orig, cnts_select, mar)

            contours.append(cnts_select)
            tagged_ims.append(imtag)


        return diffs, contours, tagged_ims

    @staticmethod
    def tag_image(image, contours, mar=0):
        """
        mar:            margin to be drawn around the tag boxes
        """ 
        img = image.copy()
        for c in contours:
            # fit a bounding box to the contour
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(img, (x-mar, y-mar), (x + w + mar, y + h + mar), (0, 255, 0), 2)
            
        return img



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
