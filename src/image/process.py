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
import pandas as pd
import imutils
import json
import shutil
import datetime as dt

class Image:
    def __init__(self, path=""):
        self.path = path
        self.img = None
        self.time = 0
        self.id = 0
        self.hash = str(0)
        self.tags = {}

    def create_dir(self, subdir):
        path = os.path.join(os.path.dirname(self.path), subdir,"")
        if not os.path.exists(path):
            os.mkdir(path)
        return path

    def copy(self, destination):
        shutil.copyfile(self.path, destination)
        self.path = destination

    def move(self, destination):
        shutil.move(self.path, destination)
        self.path = destination

    def change_path(self, destination):
        self.path = destination

    def delete(self):
        os.remove(self.path)

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

        ts = dt.datetime.fromtimestamp(os.path.getmtime(self.path))
        self.date = ts.strftime('%Y%m%d')
        self.time = ts.strftime('%H%M%S')
        self.img = raw
        self.hash = str(raw.sum())

    def read_processed(self, struct):
        for item in struct.items():
            setattr(self, item[0], item[1])
        self.read(attr="img")  

    def read(self, attr="img", file_ext=""):
        value = imageio.imread(self.change_file_ext(file_ext))
        setattr(self, attr, value)

    def change_file_ext(self, new_ext=""):
        fname, old_ext = os.path.splitext(self.path)
        if new_ext == "":
            new_ext = old_ext

        self.path = fname+new_ext
        return self.path

    def save(self, attr="img", file_ext="", remove_from_instance=False):
        if remove_from_instance:
            obj = self.__dict__.pop(attr)
        else:
            obj = getattr(self, attr)

        imageio.imwrite(self.change_file_ext(file_ext), obj)
    
    def dump_struct(self, fname, struct):
        # dump struct
        with open(os.path.join(os.path.dirname(self.path), fname + "_struct" + ".json"), "w+") as file:
            json.dump(struct, file)

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

    def read_tags(self):
        self.tags = pd.csv

    @staticmethod
    def cut_slices(image, contours, mar=0):
        """
        mar:            margin to be drawn around the tag boxes
        """
        img = image.copy()
        slices = []

        for c in contours:
            (x, y, w, h) = cv2.boundingRect(c)
            slc = img[(y-mar) : (y+mar+h), (x-mar) : (x+mar+w), :]
            slices.append(slc)
        
        return slices

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

class Series(Image):
    def __init__(self, directory="", image_list=[], struct_name="series_struct"):
        self.path = directory
        self.id = os.path.basename(self.path)
        self.struct = self.browse_subdirs_for_files("tiff")
        self.images = image_list

    def load_struct(self, struct_name):
        try:
            with open(os.path.join(self.path, struct_name+".json"), "r") as file:
                struct = json.load(file)
        except FileNotFoundError:
            struc = {}
        
        return struct

    def process_image(self, file_name, **params):
        path = os.path.join(self.path,file_name)
        i = Image(path=path)
        i.read_raw(**params)
        i.read_qr_code()
        i.delete() # removing with old path

        # create directory for Image and copy files (also updates image path)
        # delete old, save new and save structure of image
        series_dir = i.create_dir(str(i.id))
        image_dir = i.create_dir(os.path.join(str(i.id), i.time))
        i.change_path(os.path.join(image_dir, file_name)) # change path

        i.save(attr="img", file_ext=".tiff", remove_from_instance=True ) # save as tiff to new path
        i.dump_struct(file_name.split(".")[0], i.__dict__)

        return i, series_dir, image_dir

    def find_subdirs(self):
        # remove subdirectories
        return [f.name for f in os.scandir(self.path) if not f.is_file()]

    def browse_subdirs_for_files(self, file_type):
        dirs = self.find_subdirs()
        struct = {}
        for i, d in enumerate(dirs):
            f = self.find_files(subdir=d, file_type=file_type)
            assert len(f) == 1, print(f)
            path = os.path.join(self.path, d, f[0])
            struct.update({str(i):path})
        return struct

        


    def find_files(self, subdir="", file_type=""):
        # remove subdirectories
        basedir = os.path.join(self.path, subdir)
        files = [f.name for f in os.scandir(basedir) if f.is_file()]
        if file_type != "":
            # remove files that are not of type e.g. "RW2" or "tiff", etc.
            files = [i  for i in files if i.split(".")[1] == file_type]   
        
        return files

    def read_files_from_struct(self):
        images = []
        for i, struct in self.struct.items():
            img = Image()
            img.read_processed(struct)
            images.append(img)
           
        return images   

    def load_images(self, image_list):
        # import passed list
        if len(image_list) > 0:
            return image_list
        
        
        # import files from struct if exist, otherwise
        # return empty list
        if len(self.struct) == 0:
            return image_list
        
        return self.read_files_from_struct()


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
        # if len()
        if len(self.images) == 0:
            files = os.listdir(self.path)
            files = [i  for i in files if i.split(".")[1] == "RW2"]
            print(files)
        else:
            files = self.images

        images = []
        for f in files:
            i = Image(path=os.path.join(self.path,f))
            i.read_raw(**params)
            print("processed file: {}".format(f))
            i.read_qr_code()
            print("read QR code: {}".format(i.id))
            images.append(i)

        self.images = images 

    def save(self, attr):
        for i in self.images:
            i.save(attr)

    def save_list(self, imlist, name='image', file_ext='tiff'):
        for i in range(len(imlist)):
            imageio.imwrite(os.path.join(self.path,name+"_"+str(i)+"."+file_ext), imlist[i])


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

            orig_obj = self.images[ lag + i ]
            orig_img = orig_obj.img
            comp_img = self.images[i].img

            gray = cv2.cvtColor(diffs[i], cv2.COLOR_BGR2GRAY)

            #threshold the gray image to binarise it. Anything pixel that has
            #value more than 3 we are converting to white
            #(remember 0 is black and 255 is absolute white)
            #the image is called binarised as any value less than 3 will be 0 and
            # all values equal to and more than 3 will be 255
            thresh = cv2.threshold(gray, thresh_binary, 255, cv2.THRESH_BINARY)
            cnts = cv2.findContours(thresh[1], cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
            cnts = imutils.grab_contours(cnts)

            cnts_select = []
            for c in cnts:
                # fit a bounding box to the contour
                if max(c.shape) > thresh_size:            
                    cnts_select.append(c)
            
            imtag = self.tag_image(orig_img, cnts_select, mar)
            imslc1 = self.cut_slices(orig_img, cnts_select, mar)
            imslc2 = self.cut_slices(comp_img, cnts_select, mar)

            tags = {
                'contours': cnts_select,
                'slice_orig': imslc1,
                'slice_comp': imslc2,
            }

            orig_obj.tags = tags

            contours.append(cnts_select)
            tagged_ims.append(imtag)


        return diffs, contours, tagged_ims


class Session(Series):
    def __init__(self, directory):
        self.path = directory

    def read_images(self, stop_after=None, **params):
        
        files = self.find_files(file_type="RW2")

        if stop_after is None:
            stop_after = len(files)

        print('processing a total of {} files. Stopping after {} files'.format(len(files), stop_after))

        prev_id = -1
        for j, f in enumerate(files):
            # break after n images
            if j >= stop_after:
                break
            
            # read image and qr code
            image, series_dir, image_dir = self.process_image(f, **params)

            # # create empty series instance
            # if prev_id != image.id:
            #     if prev_id != -1:
            #         del subse
            #         # print("creating Series for pictures with id: {} in {}".format(i.id, subpath))
            #     subse = Series(directory=series_dir)

            # # update subseries structure
            # subse.struct.update({len(subse.struct):image.path})
            # subse.dump_struct("series", subse.struct)

            # # update session structure
            # self.struct.update({len(self.struct):subse.id})
            # self.dump_struct("session", self.struct)

            # repaort
            print("processed file: {}".format(f))
            print("read QR code: {}".format(image.id))
            
            prev_id = image.id
