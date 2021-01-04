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
import pickle
import hashlib
import shutil

class Image:
    def __init__(self, path):
        assert os.path.exists(path), print("path does not exist, working directory:", os.getcwd())
        self.path = path
        self.img = None
        self.meta = None
        self.edited = None
        self.id = 0
        self.hash = 0

    def copy(self, destination):
        shutil.copyfile(self.path, destination)
        self.path = destination

    def move(self, destination):
        shutil.move(self.path, destination)
        self.path = destination

    def read_raw(self, **params):
        """
        reads raw file using rawpy module. 
        A future version could use pillow (PIL), because of the possibility to
        read metadata better. However, RW2 files are currently not supported. 
        It is possible though to write a custom image plugin which recognizes the
        raw file.
        https://pillow.readthedocs.io/en/stable/handbook/writing-your-own-file-decoder.html
        """
        with rawpy.imread(self.path) as f:
             raw = f.postprocess(**params)

        self.img = raw
        self.hash = raw.sum()

    def save(self, what, file_ext="tiff", delete_old=False):
        what = getattr(self, what)
        imageio.imwrite(os.path.splitext(self.path)[0]+"."+file_ext, what)
        
    # def remove_original(self):
    #     os.remove(self.path)

    # def restore_original(self):
    #     self.img = self.raw

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
        self.images = image_list
        self.map = {
            "filename":[],
            "qr":[],
            "hash":[],
        }

    def update(self, new_ims):
        for im in new_ims:
            if im.hash not in self.map['hash']:
                self.images.append(im)
                self.map["filename"].append(im.path)
                self.map["qr"].append(im.id)
                self.map["hash"].append(im.hash)

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

    def read_images(self, **params):
        if len(self.images) == 0:
            files = os.listdir(self.dirpath)
            files = [i  for i in files if i.split(".")[1] == "RW2"]
            print(files)
        else:
            files = self.images

        images = []
        for f in files:
            i = Image(path=os.path.join(self.dirpath,f))
            i.read_raw(**params)
            print("processed file: {}".format(f))
            i.read_qr_code()
            print("read QR code: {}".format(i.id))
            images.append(i)

        self.images = images 

    def save(self, what):
        for i in self.images:
            i.save(what)

    def save_list(self, imlist, name='image', file_ext='tiff'):
        for i in range(len(imlist)):
            imageio.imwrite(os.path.join(self.dirpath,name+"_"+str(i)+"."+file_ext), imlist[i])


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

    def dump_pkl(self, fname="series"):
        # dump created or edited pickle file
        with open(os.path.join(self.dirpath, fname + ".pkl"), "wb") as file:
            pickle.dump(self, file)


class Session:
    def __init__(self, directory):
        self.dirpath = directory
        self.map = dict()

    def read_images(self, stop_after=None, **params):
        # remove subdirectories
        files = [f.name for f in os.scandir(self.dirpath) if f.is_file()]
        # remove files that are not "RW2"
        files = [i  for i in files if i.split(".")[1] == "RW2"]            

        if stop_after is None:
            stop_after = len(files)

        print('processing a total of {} files. Stopping after {} files'.format(len(files), stop_after))

        prev_id = -1
        for j, f in zip(range(len(files)), files):
            # break after n images
            if j >= stop_after:
                break
            
            # read image and qr code
            f_name = os.path.join(self.dirpath,f)
            i = Image(path=f_name)
            i.read_raw(**params)
            i.read_qr_code()

            print("processed file: {}".format(f))
            print("read QR code: {}".format(i.id))

            # create dictionary for Series and copy files (also updates image path)
            subpath = os.path.join(self.dirpath, str(i.id))
            if not os.path.exists(subpath):
                os.mkdir(subpath)

            i.move(os.path.join(subpath, f))

            # open existing series pickle file if exisits, otherwise create empty series
            if prev_id != i.id:
                if prev_id != -1:
                    del subse
                try:
                    with open(os.path.join(subpath, "series.pkl"), "rb") as file:
                        subse = pickle.load(file)
                except FileNotFoundError:
                    print("creating Series for pictures with id: {} in {}".format(i.id, subpath))
                    subse = Series(directory=subpath, image_list=[])

            # add all images not exisiting in hash dictionary
            subse.update([i])
            # update map
            self.map.update({str(i.id):subse.map})

            # dump created or edited pickle file
            subse.dump()

            prev_id = i.id

        # store session
        with open(os.path.join(self.dirpath, "session.pkl"), "wb") as file:
            pickle.dump(self, file)