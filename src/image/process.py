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
# from pyzbar import pyzbar
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import imutils
import json
import shutil
import datetime as dt
from exifread import process_file
from utils.manage import Files

class Image(Files):
    def __init__(self, path="", import_image=True):
        self.path = path
        self.img = None
        self.time = 0
        self.id = 0
        self.hash = str(0)
        self.tags = {}
        self.analyses = {}

        self.read_struct(import_image)

    def read_raw(self, **params):
        """
        reads raw file using rawpy module. 
        with exifread. Reading Metadata is super easy.
        """
        with rawpy.imread(self.path) as f:
             raw = f.postprocess(**params)

        # get image time
        img_time = self.get_meta(tag="EXIF DateTimeOriginal")
        ts = dt.datetime.strptime(img_time.values, "%Y:%m:%d %H:%M:%S")
        self.date = ts.strftime('%Y%m%d')
        self.time = ts.strftime('%H%M%S')

        self.img = raw
        self.hash = str(raw.sum())

    def get_meta(self, tag=""):
        with open(self.path, 'rb') as f:
            tags = process_file(f)

        return tags[tag]

    def read_struct(self, import_image=True):
        if not os.path.exists(self.path):
            print("Path does not exist. Check spelling.")
            return

        if os.path.isdir(self.path):
            try:
               sname = self.find_single_file(directory=self.path, file_type="json")
            except AssertionError:
                print("Did not import {} correctly. more than one structure in image folder".format(self.path))
        else:
            sname = self.append_to_filename(self.path, "_struct.json")

        try:
            with open(sname, "r") as f:
                struct = json.load(f)
            self.read_processed(struct, import_image)

        except FileNotFoundError:
            print("no struct json file found. Proceeding without")

    def read_processed(self, struct, import_image):
        for item in struct.items():
            setattr(self, item[0], item[1])

        if import_image:
            self.read_image(attr="img")  

    def dump_struct(self, struct):
        # dump struct
        dirname = os.path.dirname(self.path)
        filename = os.path.basename(self.path).split(".")[0] + "_struct"
        extname = ".json"

        print(dirname, filename, filename+extname)
        with open(os.path.join(dirname, filename + extname), "w+") as file:
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
            # code = pyzbar.decode(thresh)[0]
            # message = code.data.decode("utf-8")
            detector = cv2.QRCodeDetector()
            message, bbox, _ = detector.detectAndDecode(thresh)
            # print(message, bbox, _)
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

    def show(self):
        plt.imshow(self.img)
        plt.axis('off')

    
    @staticmethod
    def get_center_2D(img):
        assert len(img.shape) == 2 or len(img.shape) == 3, "img has wrong number of dimensions"
        y = round(img.shape[0]/2)
        x = round(img.shape[1]/2)
        return x, y

    @staticmethod
    def draw_cross(img, x, y, size, color):
        ybar = range(max(0,y-size), min(y+size+1, img.shape[0]))
        xbar = range(max(0,x-size), min(x+size+1, img.shape[1]))
        if len(img.shape) == 3:
            img[y,xbar] = color # midpoint
            img[ybar,x] = color # midpoint

        if len(img.shape) == 2:
            assert len(color) == 3, "probably greyscale image. Color should be int, recommended: 0 or 255"
            img[y,xbar] = color # midpoint
            img[ybar,x] = color # midpoint
        
        return img

    @classmethod
    def draw_center_cross(cls, img, size=1, color=(255,0,0)):
        x, y = cls.get_center_2D(img)
        return cls.draw_cross(img, x, y, size, color)


class Series(Image):
    def __init__(
        self, 
        directory="", 
        image_list=[], 
        struct_name="series_struct",
        import_image=True
        ):
        self.path = directory
        self.id = os.path.basename(self.path)
        self.struct = self.browse_subdirs_for_files(directory, "tiff")
        self.images = self.read_files_from_struct(import_image)

    def process_image(self, file_name, delete_old=False, **params):
        path = os.path.join(self.path,file_name)
        i = Image(path=path)
        i.read_raw(**params)
        i.read_qr_code()
        if delete_old:
            i.delete() # removing with old path

        # create directory for Image and copy files (also updates image path)
        # delete old, save new and save structure of image
        series_dir = i.create_dir(str(i.id))
        image_dir = i.create_dir(os.path.join(str(i.id), i.time))
        i.change_path(os.path.join(image_dir, file_name)) # change path

        i.save(attr="img", file_ext=".tiff", remove_from_instance=True ) # save as tiff to new path
        i.dump_struct(i.__dict__)

        return i, series_dir, image_dir

    def read_files_from_struct(self, import_image):
        images = []
        for i, path in self.struct.items():
            img = Image(path)
            img.read_struct(import_image)
            images.append(img)
           
        return images   

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

class Session(Series):
    def __init__(self, directory):
        self.path = directory

    def read_images(self, stop_after=None, file_number=None, 
                    delete_old=False, params={}):
        
        files = Files.find_files(self.path, file_type="RW2")

        if file_number is not None:
            files = [files[file_number]]
            stop_after = 1
        else:        
            if stop_after is None:
                stop_after = len(files)
        
        print('processing a total of {} files. Stopping after {} files'.format(
            len(files), stop_after))

        for j, f in enumerate(files):
            # break after n images
            if j >= stop_after:
                break
            print("processing file: {}".format(f))
            
            # read image and qr code
            image, series_dir, image_dir = self.process_image(
                f, delete_old=delete_old, **params)

            # report
            print("read QR code: {}".format(image.id))