# author: Florian Schunck
# date: 14.11.2020
#
# Descritption:
# Class for image analysis of nanocosm image files (RAW)
# containing methods for cropping, difference of continuous images, edge detection

import os
import warnings
import hashlib
from PIL import Image
import cv2
import gc
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from datetime import datetime as dt

from peek.utils.manage import Files

class Snapshot(Files):
    """
    class for handling images
    """

    def __init__(self, path: str = "", meta: dict = {}):
        self._meta = None
        self._hash = None
        self.img = None
        self.pixels = np.array([])
        self.tags = {}
        self.annotations = None
        self.analyses = {}
        
        self.read(path)
        self.calculate_pixels()
        self.set_meta(meta)

        for m in ["id", "date", "time",]:
            if m is None:
                warnings.warn(f"metadata {m} is undefined. Set this attribute with meta={{'m': ...}}")

    def __repr__(self):
        return f"{str(self.img)} @ {self.path}"

    def __hash__(self):
        return self._hash

    @property
    def time(self):
        return self._meta.get("time")

    @property
    def date(self):
        return self._meta.get("date")

    @property
    def id(self):
        return self._meta.get("id")

    @property
    def name(self):
        interpunct = [";", ":", "-", ".", ",", " "]
        name = f"{self.date}_{self.time}_{self.id}"
        for i in interpunct:
            name = name.replace(i, "")
        return name

    @property
    def metadata(self):
        return dict(self._meta.items())

    @property
    def path(self):
        return self.img.filename

    @property
    def filename(self):
        name, _ = os.path.splitext(os.path.basename(self.path))
        return name

    @property
    def size(self):
        return (self.img.size[1], self.img.size[0], self.img.layers)

    def read(self, path):
        self.img = Image.open(os.path.normpath(os.path.abspath(path)))
        self._meta = self.img.getexif()
        print(f"read {self.path}")

    def set_meta(self, meta: dict):
        self._meta.update(meta)

    def calculate_pixels(self):
        self.pixels = np.asarray(self.img)
        self._hash = hashlib.md5(self.pixels.tobytes()).hexdigest()

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
            tags = exifread.process_file(f)
        
        tags = tags[tag].values
        
        if index is not None:
            tags = tags[index]

        if return_as is not None:
            tags = return_as(tags)

        return tags


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
        img_time = dt.strptime(self.time, "%H%M%S")
        midnight = 0
        night = [dt.strptime(str(start_night_h),'%H'), 
                 dt.strptime(str(midnight), '%H'),
                 dt.strptime(str(end_night_h),'%H')]
    	
        if night[0] < img_time < night[1] or night[1] < img_time < night[2]:
            atnight = True
        else:
            atnight = False

        return atnight

    def process_image(self, file_name, delete_old=False, qr_thumb=False, 
                      qr_params={}, output_format="tiff", **params):
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
            # save as tiff to new path
            self.save(attr="qr_thumb", file_ext="_qr.jpeg", 
                      remove_from_instance=True, modify_path=False) 
        else:
            del self.qr_thumb
        self.save(attr="img", file_ext="."+output_format, remove_from_instance=True ) # save as tiff to new path
        self.dump_struct(self.__dict__)

        return self, series_dir, image_dir

    # def read_tags(self):
    #     self.tags = pd.csv

    def post_process_tags(self, func, fileobjects):
        """
        function to postprocess image tags with custom function
        """
        objects = [getattr(self.tags, fo) for fo in fileobjects]
        for tag_objs in zip(*objects):
            func(self, tag_objs)



    def cut_slices(self, mar=0):
        """
        mar:  margin to be drawn around the tag boxes
        """        
        return self._cut_slices(
            pixel_img=self.pixels, 
            mar=mar)

    def _cut_slices(self, pixel_img, mar=0, max_from_center=False):
        """
        method for slicing a different image with the same contours

        pixel_img:      image to be sliced
        contours:       list of contours making the slices
        mar:            margin to be drawn around the tag boxes
        """
        slices = []
        for c in self.contours:
            x, y, w, h = cv2.boundingRect(c)
            if max_from_center:
                x, y = contour_center(c)
                x = int(np.floor(x))
                y = int(np.floor(y))
                w, h = (1, 1)

            # add margin to bounding mox
            slc = self.slice_image(pixel_img, x, y, w, h, mar)
            slices.append(slc)
        
        return slices

    @staticmethod
    def slice_image(img, x, y, w, h, mar=0):
        if len(img.shape) == 3:
            return img[(y-mar) : (y+mar+h), (x-mar) : (x+mar+w), :]
        if len(img.shape) == 2:
            return img[(y-mar) : (y+mar+h), (x-mar) : (x+mar+w)]

        raise ValueError(f"dimension of image was not 2 or 3 but {img.shape}")

    def tag_image(self, mar=0):
        """
        mar:            margin to be drawn around the tag boxes
        """ 
        img = self.pixels.copy()
        for c in self.contours:
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


def contour_center(contour):
    x, y, w, h = cv2.boundingRect(contour)
    xcenter = x + w / 2
    ycenter = y + h / 2
    return xcenter, ycenter


def threshold_imgage_to_idstring(img):
    img_colors = np.unique(img)
    assert img.ndim == 2, "only 2D images can be used"
    assert 0 in img_colors, "zero not in image colors"
    assert len(img_colors) == 2, "image had more than 3 colors, only thresholded images can be used"

    threshold_pixels = np.where(img.flatten() != 0)[0]

    return array1d_to_string(threshold_pixels)

def array1d_to_string(a):
    return str(a.tolist()).replace("[", "").replace("]", "").replace(",", "")

def string_to_array1d(s):
    return np.fromstring(s, sep=" ", dtype=int)

def idstring_to_threshold_image(s, margin):
    a = string_to_array1d(s)
    
    shape = margin_to_shape(mar=margin)
    flat_img = np.zeros((np.multiply(*shape)), dtype=np.uint8)

    flat_img[a] = 255

    return flat_img.reshape(shape)


def margin_to_shape(mar):
    return (1 + mar * 2, 1 + mar * 2)

def get_tag_box_coordinates(self, contour):
    x, y, w, h = cv2.boundingRect(contour)


class Series():
    def __init__(
        self, 
        images: list = []
    ):
        self.id = self.get_unique(images, "id")
        self.date = self.get_unique(images, "date")
        self.images = images

    @staticmethod
    def get_unique(images: list, key: str):
        unq = np.unique([getattr(img, key) for img in images])
        assert len(unq) == 1, f"no unique ids {unq} in series"
        return unq[0]

    @property
    def pixels(self):
        return [i.pixels for i in self.images]

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