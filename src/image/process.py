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
import gc
# from pyzbar import pyzbar
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import imutils
import json
import shutil
from datetime import datetime as dt
from exifread import process_file
from utils.manage import Files

class Image(Files):
    def __init__(self, path="", import_image=True, ignore_struct_path=False):
        self.path = path
        self.img = None
        self.time = 0
        self.id = 0
        self.hash = str(0)
        self.tags = {}
        self.analyses = {}

        self.read_struct(import_image, ignore_struct_path)

    def read_raw(self, **params):
        """
        reads raw file using rawpy module. 
        with exifread. Reading Metadata is super easy.
        """
        with rawpy.imread(self.path) as f:
             raw = f.postprocess(**params)

        # get image time
        img_time = self.get_meta(tag="EXIF DateTimeOriginal")
        ts = dt.strptime(img_time, "%Y:%m:%d %H:%M:%S")
        self.date = ts.strftime('%Y%m%d')
        self.time = ts.strftime('%H%M%S')
        self.atnight = self.image_at_night(start_night_h=21, end_night_h=6)
        self.img = raw
        self.hash = str(raw.sum())

        # get additional metadata (depends on tags, to see which tags can be
        # accessed try get_meta.py with a sample image)
        self.iso = self.get_meta(tag="Image Tag 0x0037", index=0, return_as=str)
        self.focal_length = self.get_meta(tag="EXIF FocalLength", index=0, return_as=str)
        self.exposure_time = self.get_meta(tag="EXIF ExposureTime", index=0, return_as=str)
        self.f_value = self.get_meta(tag="EXIF FNumber", index=0, return_as=str)
        self.max_aperture = self.get_meta(tag="EXIF MaxApertureValue", index=0, return_as=str)
        camera = self.get_meta(tag="Image Make", return_as=str)
        model = self.get_meta(tag="Image Model", return_as=str)
        self.camera = " ".join([camera, model])

    def get_meta(self, tag="", index=None, return_as=None):
        with open(self.path, 'rb') as f:
            tags = process_file(f)
        
        tags = tags[tag].values
        
        if index is not None:
            tags = tags[index]

        if return_as is not None:
            tags = return_as(tags)

        return tags

    def read_struct(self, import_image, ignore_struct_path):
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
            self.read_processed(struct, import_image, ignore_struct_path)

        except FileNotFoundError:
            print("no struct json file found. Proceeding without")

    def read_processed(self, struct, import_image, ignore_struct_path):
        if ignore_struct_path:
            del struct['path']
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

    def read_qr_code(
        self, rqr=None, threshold={'r':30,'g':30,'b':30}, 
        night_id='999', error_id='999', 
        extract_fun="extract_id", extract_kwds={}
        ):
        """
        Cut slice from image, where the QR code is expected, then go on and 
        carry out a range of image processing methods and try to detect always in
        between steps. If detection was unsuccessful after all attempts, it
        is checked if the image was taken at night (automatic 24 hr pictures)
        and assigns a pre determined id to that picture.
        ATTENTION: The ID is extracted based on a custom function based on the

        rqr          dict: bounding box of expected QR Code region 
                     (top, bottom, left, right). Defaults to the whole image
        threshold    dict: numpy array to specify the threshold for QR code 
                     Either length 1 for grayscale or length 3 for RGB pictures
        night_id     str: id of images which were always taken at night and are 
                     therfore unreadable
        error_id     id which is assigned to images which cannot be read
        extract_fun  str: method name of Image class. Depends on the QR code
                     extracts the id which is the second part of a string
                     separated by "_" (e.g.: NANO_2)
        extract_kwds dict: additional keyword arguments passed to extract_fun
        """
        # import variables
        extract = getattr(self, extract_fun, self.extract_id)

        if rqr is None:
            t, l = (0, 0)
            b, r = self.img.shape[:2]
        else:
            t, b, l, r = rqr.values()

        threshold = np.array(list(threshold.values()))
        # improve image 
        imo = self.img.copy()[t:b, l:r,:]
        im = 255-cv2.inRange(imo, np.array([0,0,0]), threshold)
        
        # first detection attempt
        message = self.detect(im)
        img_id = extract(message, error_id, **extract_kwds)
        
        # second attempt after passing through MIN filter
        if img_id == error_id:
            gc.collect()
            im = self.min_filter(5, im)
            message = self.detect(im)
            img_id = extract(message, error_id, **extract_kwds)

        # second attempt after passing through MAX filter
        if img_id == error_id:
            gc.collect()
            im = self.max_filter(3, im)
            message = self.detect(im)
            img_id = extract(message, error_id, **extract_kwds)

        # third attempt. Iterate over original image 
        if img_id == error_id:
            gc.collect()
            imos = cv2.resize(imo, (0,0), fx=0.3, fy=0.3)
            for r in range(0,10):

                upper = np.array([0,0,0]) + r*10
                im = 255-cv2.inRange(imos, np.array([0,0,0]), upper)
                im = self.min_filter(3, im)

                message = self.detect(im)
                img_id = extract(message, error_id, **extract_kwds)

                if message != "":
                    break
        
        # if nothing works. Check if the image was taken at night
        if img_id == error_id and self.atnight:
            img_id = night_id

        self.id = img_id
        self.qr_thumb = cv2.resize(imo, (0,0), fx=0.1, fy=0.1)
    
    @staticmethod
    def extract_id(message, error_id='999'):
        if message == "error":
            return error_id
        
        try:
            parts = message.split(sep="_")
            nano_id = parts[1].zfill(2)
        except IndexError:
            nano_id = error_id

        return nano_id

    @staticmethod
    def detect(image):
        gc.collect()
        try:
            detector = cv2.QRCodeDetector()
            message, bbox, _ = detector.detectAndDecode(image)
        except:
            message = "error"
        
        return message

    def image_at_night(self, start_night_h=21, end_night_h=5):
        night = [dt.strptime(str(start_night_h),'%H'), 
                 dt.strptime(str(end_night_h),'%H')]

        if night[0] < dt.strptime(self.time, "%H%M%S") < night[1]:
            atnight = True
        else:
            atnight = False

        return atnight

    def process_image(self, file_name, delete_old=False, qr_thumb=False, 
                      qr_params={}, **params):
        self.read_raw(**params)
        self.read_qr_code(**qr_params)
        if delete_old:
            self.delete() # removing with old path

        # create directory for Image and copy files (also updates image path)
        # delete old, save new and save structure of image
        series_dir = self.create_dir(self.id)
        image_dir = self.create_dir(os.path.join(self.id, self.time))
        self.change_path(os.path.join(image_dir, file_name)) # change path
        
        if qr_thumb:
            self.save(attr="qr_thumb", file_ext=".jpeg", remove_from_instance=True ) # save as tiff to new path
        else:
            del self.qr_thumb
        self.save(attr="img", file_ext=".tiff", remove_from_instance=True ) # save as tiff to new path
        self.dump_struct(self.__dict__)

        return self, series_dir, image_dir

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

    @staticmethod
    def max_filter(n, img):
        size = (n, n)
        shape = cv2.MORPH_RECT
        kernel = cv2.getStructuringElement(shape, size)

        return cv2.dilate(img, kernel)

    @staticmethod
    def min_filter(n, img):
        size = (n, n)
        shape = cv2.MORPH_RECT
        kernel = cv2.getStructuringElement(shape, size)

        # Applies the minimum filter with kernel NxN
        return cv2.erode(img, kernel)


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

    def read_files_from_struct(self, import_image):
        images = []
        for i, path in self.struct.items():
            img = Image(path)
            # img.read_struct(import_image)
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
            i = Image(path=os.path.join(self.path, f))
            image, series_dir, image_dir = i.process_image(
                f, delete_old=delete_old, **params)

            # report
            print("read QR code: {}".format(image.id))
            
            del image
            gc.collect()