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
import json
import shutil

class Image:
    def __init__(self, path=""):
        self.path = path
        self.img = None
        self.time = 0
        self.id = 0
        self.hash = str(0)
        self.tags = {}


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

        self.time = os.stat(self.path).st_mtime
        self.img = raw
        self.hash = str(raw.sum())

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
    
    def read(self, attr="img", file_ext=""):
        value = imageio.imread(self.change_file_ext(file_ext))
        setattr(self, attr, value)

    # def save_pkl(self, attr):
    #     obj = getattr(self, attr)
    #     direc = os.path.dirname(self.path)
    #     fname = os.path.basename(self.path).split(".")[0]
    #     path = os.path.join(direc, attr + "_" + fname + ".pkl")
    #     print(path)
    #     with open(path, "wb") as file:
    #         pickle.dump(obj, file)

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

    # def read_something_from_file(self, something):
    #     direc = os.path.dirname(self.path)
    #     fname = os.path.basename(self.path).split(".")[0]
    #     path = os.path.join(direc, something + "_" + fname + ".pkl")
    #     if os.path.exists(path):
    #         with open(path, "rb") as f:
    #             self.tags = pickle.load(f)
    #     else:
    #         print("error", path)


    def annotate(self):
        pass

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
        self.dirpath = directory
        self.struct = self.load_struct(struct_name)
        self.images = self.load_images(image_list)

    def load_struct(self, struct_name):
        try:
            with open(os.path.join(self.dirpath, struct_name+".json"), "r") as file:
                m = json.load(file)
        except FileNotFoundError:
            m = {}
        
        return m

    def read_files_from_struct(self):
        images = []
        for i, struc in self.struct.items():
            img = Image()
            for item in struc.items():
                setattr(img, item[0], item[1])
            img.read(attr="img")  
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

    def save(self, attr):
        for i in self.images:
            i.save(attr)

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


    def dump(self, fname="series"):
        # dump struct
        with open(os.path.join(self.dirpath, fname + "_struct" + ".json"), "w+") as file:
            json.dump(self.struct, file)


class Session:
    def __init__(self, directory):
        self.dirpath = directory
        self.struct = dict()

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

            # DONE: convert to tiff and delete old
            i.delete() # removing with old path
            i.change_path(os.path.join(subpath, f)) # change path
            i.save(attr="img", file_ext=".tiff", remove_from_instance=True ) # save as tiff to new path

            # create empty series instance
            if prev_id != i.id:
                if prev_id != -1:
                    del subse
                    print("creating Series for pictures with id: {} in {}".format(i.id, subpath))
                
                # try opening series struct, if it does not exist create empty struct
                subse = Series(directory=subpath, image_list=[])


            # update subseries_struct
            subse.struct.update({str(len(subse.struct)):i.__dict__})
            # update struct
            self.struct.update({str(i.id):subse.struct})

            # dump created struct file
            subse.dump()

            prev_id = i.id

        # store session
        with open(os.path.join(self.dirpath, "session.json"), "w+") as file:
            json.dump(self.struct, file)
