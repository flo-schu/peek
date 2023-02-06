import os
import sys
import time
from copy import copy
import imageio
from functools import lru_cache
import cv2 as cv
import pandas as pd
import numpy as np
import tqdm
import matplotlib as mpl
from datetime import datetime
from matplotlib import rc
from matplotlib import pyplot as plt
from matplotlib.backend_bases import _Mode
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from matplotlib.widgets import RectangleSelector, Slider
from scipy.ndimage import gaussian_filter1d
from scipy.signal import argrelextrema, find_peaks

from peek.utils.manage import Files
from peek.image.process import (
    Snapshot, idstring_to_threshold_image, contour_center, 
    threshold_imgage_to_idstring)

rc("font", family='monospace', size=9)


class Tag(Files):
    def __init__(self, props: dict={}):

        # tag attributes which are saved to df
        # IF POSSIBLE NEVER CHANGE THESE NAMES. WHY?
        # THEN THE DATA WILL BE HOMOGENEOUSLY NAMED ACCROSS ALL ANALYSES
        # ----------------------------------------------------------------------
        self.image_hash = None       # unique reference hash of parent image
        self.id = 0                  # id of tag in image
        self.filtered = 0            # indicates if the tag was pre-filtered
        self.x = 0                   # top left corner of bounding box (x-axis)
        self.y = 0                   # top left corner of bounding box (y-axis)
        self.width = 0               # width of bounding box
        self.height = 0              # height of bounding box
        self.label = ""              # label of manual classification
        self.time = ''               # time of detection
        self.analysis = 'none'       # name of analysis 
        self.annotated = False       # was the label manually annotated
        self.xcenter = 0             # x-coordinate of center of detected object
        self.ycenter = 0             # y-coordinate of center of detected object
        self.img_path = ""           # path of original image
        self.tag_box_thresh_ids = "" # string of ids where threshold was exceeded
        # ----------------------------------------------------------------------
        
        # initiate Tag with properties if props dictionary is given
        if len(props) > 0:
            self.set_tag(props)
        

    def set_tag(self, props):
        for key, value in props.items():
            setattr(self, key, value)
   
    def unpack_dictionaries(self):
        pop_dicts = []
        for key, item in self.__dict__.items():
            if isinstance(item, dict):
                pop_dicts.append(key)
        
        for d in pop_dicts:
            for key, value in self.__dict__.pop(d).items():
                setattr(self, key, value)

    def save(self):
        """
        adds current time and converts to pd.Series
        """
        self.time = time.strftime('%Y-%m-%d %H:%M:%S')
        tag = self.__dict__.copy()
        return pd.Series(tag)

    @property
    def margin(self):
        assert self.width == self.height
        return int((self.width - 1) / 2)

    @property
    def threshold_img(self):
        return idstring_to_threshold_image(
            self.tag_box_thresh_ids, 
            shape=(self.height, self.width))

    @property
    def slice(self):
        x = slice(self.x, self.x + self.width)
        y = slice(self.y, self.y + self.height)
        return y, x

    @property
    def orig_img(self):
        img = self.load_img(self.img_path)
        return img[self.slice]

    @staticmethod
    @lru_cache
    def load_img(path):
        return imageio.imread(path)

# interactive figure
class Annotations(Tag): 
    def __init__(
        self, 
        path,
        image=None, 
        new_tags=None,
        detector=None,
        image_metadata={},
        analysis="undefined", 
        tag_db_path="annotations/tag_db.csv", 
        keymap={
            'd':"Daphnia Magna",
            'c':"Culex Pipiens, larva",
            'p':"Culex Pipiens, pupa",
            'u':"unidentified"
            },
        extra_images = [],
        sliders=[],
        zfill=0,
        continue_annotation=True,
        classifier=None,
    ):
        self.path = os.path.normpath(path)
        self.analysis = analysis
        self.new_tags = new_tags
        self.tags = self.load_processed_tags()
        self.detector = detector
        self.classifier = classifier
        self.image = self.load_image(image, image_metadata)
        self.image_hash = self.image.__hash__()
        self.display_whole_img = False
        self.tag_db_path = tag_db_path
        self.origx = (0,0)
        self.origy = (0,0)
        self.xlim = (0,0)
        self.ylim = (0,0)
        self.ctag = None
        self.i = 0
        self.last_tag_number = 0
        self.error = (False, "no message")
        self.keymap = keymap
        self.zfill = zfill
        self.target = ()
        self.selector = None
        self.sliders = {}
        self._pc = None
        self._extra_images = extra_images
        self._continue_annotation = continue_annotation
        # plot axes
        self.ax_complete_fig = None
        self.axes_tag = [None, None, None, None]
        self.axes_slider = []
        
        # read tags if supplied
        if self.new_tags is not None:
            self.read_new_tags(self.new_tags)

        self._tag_filter = list(self._tags.index)
        self._manual_ids = []
        self._slider_parameters = sliders
        self.apply_tag_filter()

    @property
    def tags(self):
        # first if clause is necessary for creating of instance
        if not hasattr(self, "_tag_filter"):
            return self._tags
        return self._tags.loc[self._tag_filter + self._manual_ids, :]

    @tags.setter
    def tags(self, tags):
        assert isinstance(tags, pd.DataFrame)
        self._tags = tags
        assert all(tags["id"] == tags.index), "mismatch of id with index in tags"

    def load_image(self, image, meta): 
        if image is None:
            img_path = self.tags.img_path.unique()
            assert len(img_path) == 1, f"multiple image paths in annotation {img_path}"
            return Snapshot(img_path[0], meta=meta)
        else:
            assert isinstance(image, Snapshot)
            return image

    def get_image_path(self):
        img_path = self.tags.img_path.unique()
        assert len(img_path) == 1, f"multiple images listed in annotation file {img_path}"
        return img_path[0]

    def start(self, plot_type="plot_complete_tag_diff"):
        """
        plot_type   one of "plot_complete_tag_diff", "plot_tag", "plot_tag_diff"
        """
        self.figure = plt.figure(figsize=(12,6))
        self.figure.subplots_adjust(left=.15, hspace=.1, bottom=0.05, right=.95)
        self.figure.canvas.mpl_connect('key_press_event', self.press) 
        self.figure.canvas.mpl_connect('button_press_event', self.click_callback) 
        mpl.rcParams['keymap.back'] = ['left'] 
        mpl.rcParams['keymap.pan'] = [] 
        mpl.rcParams['keymap.pan'] = [] 
        
        # create figure
        init_plot = getattr(self, plot_type)
        init_plot()
        self.set_plot_titles()

        plt.ion()
        self.draw_tag_boxes()
        self.show_tag_number(0)
        self.figure.show()

    def test(self):
        
        # for testing
        class A:
            def __init__(self, key="u"):
                self.key = key

        ax = self.ax_complete_fig
        class B:
            def __init__(self, button = 3, xdata = 100, ydata = 200, dblclick=False):
                self.button = button
                self.xdata = xdata
                self.ydata = ydata
                self.inaxes = ax

        self.click_callback(B(1, xdata=891, ydata=530, dblclick=False))
        self.press(A())
        self.click_callback(B())

        self.sliders["max_clusters"][1](2)
        self.sliders["max_clusters"][1](3)

        self.click_callback(B(xdata=500))
        self.press(A("n"))
        self.press(A("d"))
        self.click_callback(B(1, xdata=891, ydata=200, dblclick=False))
        self.sliders["max_clusters"][1](10)

    # def test(self, eclick=(1750, 800), erelease=(1770, 810)):
    def select_callback(self, eclick, erelease):
        """
        Callback for line selection.

        *eclick* and *erelease* are the press and release events.
        """
        x1, y1 = int(eclick.xdata), int(eclick.ydata)
        x2, y2 = int(erelease.xdata), int(erelease.ydata)
        tag_contour = np.array([[[x1, y1]], [[x2, y2]]])
        
        self.manual_tag(contour=tag_contour, mar=0)
    
    def click_callback(self, event):
        """
        Callback for line selection.

        *eclick* and *erelease* are the press and release events.
        """
        toolbar_mode = self.figure.canvas.toolbar.mode
        if toolbar_mode == _Mode.ZOOM:
            return

        if event.inaxes == self.ax_complete_fig:
            if not self.selector.active:
                if event.button == 3:

                    # print(event)
                    x, y = int(event.xdata), int(event.ydata)
                    # print(x, y)
                    tag_contour = np.array([[[x, y]]])
                    
                    self.manual_tag(contour=tag_contour, mar=self.detector.margin)

                if event.button == 1:
                    x, y = int(event.xdata), int(event.ydata)
                    tag_id = self.get_tag_id_of_closest_point(x, y)

                    self.last_tag_number = self.i
                    self.show_tag_number(i=self.get_tag_number_from_id(tag_id))

    class slider_callback():
        # works okay, but the problem is that images will be copied or not
        # better would be to query the tags for the relevant indices. Would
        # also be faster
        def __init__(self, annotations, param):
            self.annotations = annotations
            self.param = param      

        def __call__(self, val):
            setattr(self.annotations.detector, self.param, val)
            self.annotations.apply_tag_filter()

    def get_tag_id_of_closest_point(self, x, y):
        diff = np.array([self.tags['ycenter']-y, self.tags["xcenter"]-x])
        closest = np.abs(diff).sum(axis=0).argsort()[0]
        return int(self.tags.iloc[closest]["id"])
    
    def apply_tag_filter(self):
        kept_tags = self.detector.filter_tags(self.new_tags)
        self._tag_filter = kept_tags
        self._tags["filtered"] = [0 if t in kept_tags else 1 for t in self._tags["id"]]
        self.save_progress()

        if self._pc is not None:
            self._pc.remove()  # remove tags boxes (Artis)
            self.draw_tag_boxes()

    def manual_tag(self, contour, mar=0):
        t = Tag()
        x, y, w, h = cv.boundingRect(contour)
        
        # manually add margins
        x = x - mar
        y = y - mar
        w = w + 2 * mar
        h = h + 2 * mar

        t.image_hash = self.image_hash
        t.img_path = self.image.path
        t.id = len(self._tags)
        t.x = x
        t.y = y
        t.width = w
        t.height = h
        t.label = "?"
        t.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        t.analysis = "manual"
        t.annotated = False
        t.xcenter, t.ycenter = contour_center(contour)

        # get closest neighbor
        max_dist = np.sqrt(2 * self.detector.margin ** 2)
        t.closest_neighbor = self.detector.find_neighbors(
            t.__dict__, self.new_tags, max_dist)
        
        # analyze the new tag
        self.analyze_manual_tag(tag=t)
        new_tag = t.save()

        print(f"created new manual tag {t}")

        self._tags = pd.concat([self._tags, new_tag.to_frame().T], ignore_index=True)

        self._manual_ids.append(t.id)
        self._pc.remove()
        self.draw_tag_boxes()
        self.save_progress()

    def analyze_manual_tag(self, tag):
        orig_slice = self.image.pixels[tag.slice]
        comp_slice = self.image.comparison[tag.slice]
        thresh = self.detector.thresholding(orig_slice, comp_slice)
        tag.tag_box_thresh_ids = threshold_imgage_to_idstring(thresh)
        nb = self.read_tag(self.tags, tag.closest_neighbor)
        props = self.detector.analyze_tag(
            tag=tag.__dict__, neighbor=(nb.id, nb.__dict__))
        _ = [setattr(tag, key, value) for key, value in props.items()]
        

    def plot_complete_tag_diff(self):
        self.display_whole_img = True
        self.origx = (0, self.image.img.size[0])
        self.origy = (self.image.img.size[1],0)
        n_sliders = len(self._slider_parameters)
        self.gs = plt.GridSpec(
            nrows=4 + n_sliders, ncols=4, 
            width_ratios=[1, 1, 0.8, 0.8],
            height_ratios=[1, 0.2, 1] + [0.2] + [0.5 / n_sliders] * n_sliders
        )


        self.ax_complete_fig = self.figure.add_subplot(self.gs[0:3, 0:2])

        self.axes_tag[0] = self.figure.add_subplot(self.gs[0, 2])
        self.axes_tag[1] = self.figure.add_subplot(self.gs[0, 3])

        for i, tit in enumerate(self._extra_images):
            self.axes_tag[i+2] = self.figure.add_subplot(self.gs[2, i+2])

        # create slider axes
        for i in range(n_sliders):
            self.axes_slider.append(self.figure.add_subplot(self.gs[4 + i,:]))

        self.show_original()
        self.show_sliders()

    def plot_tag(self):
        self.axes_tag = [
            self.figure.add_subplot(111)
        ]

    def plot_tag_diff(self):
        self.axes_tag = [
            self.figure.add_subplot(121),
            self.figure.add_subplot(122),
        ]

    def set_plot_titles(self):
        self.axes_tag[0].set_title("original")
        self.axes_tag[1].set_title("threshold")

        for i, tit in zip(range(2,4), self._extra_images):
            self.axes_tag[i].set_title(tit)
        
    def load_processed_tags(self):
        try:
            tags = pd.read_csv(self.path)
            
            analysis = tags.analysis.unique()
            if len(analysis) > 1:
                is_manual = analysis == "manual"
                if any(is_manual) and len(is_manual) == 2:
                    analysis = analysis[~is_manual]
                else:
                    raise ValueError(f"multiple analyses in .csv file {analysis}")
            
            # overwrite new index with id
            tags.index = tags.id
            self.analysis = analysis[0]
            
            return tags
        except FileNotFoundError:
            print(f"no existing tags found at {self.path}. Starting new tags")
            return pd.DataFrame({'id':[]})

    def load_processed_tags_from_tar(self, tar):
        try:
            pd.read_csv(tar.extractfile(self.path))
        except FileNotFoundError:
            print(f"no existing tags found. Starting new file on {self.path}")
            return pd.DataFrame({'id':[]})

    def update_ctag(self, attr, value):
        """
        updates tags in tags dataframe
        """
        tid = self.ctag.id
        # updates the attribute of ctag
        setattr(self.ctag, attr, value)

        # updates the cell in the database (access _tags directly)
        self._tags.loc[tid, attr] = value


    def press(self, event):
        print('press', event.key)
        sys.stdout.flush()
        if event.key in self.keymap.keys():
            self.update_ctag("label", self.keymap[event.key])
            self.update_ctag("annotated", True)
            t = self.ctag.save()
            # self.drop_duplicates()
            # self.tags = pd.concat([self.tags, t.to_frame().T], ignore_index=True)
            self.save_tag_to_database(t)

            # self.tags = self.tags.sort_values(by='id')
            self.save_progress()

            # directly go to next tag after labeling
            self.reset_lims()
            self.show_next_tag()

        if event.key == "r":
            self.reset_lims()
            self.show_tag_number(self.last_tag_number)
        
        if event.key == "n":
            self.reset_lims()
            self.show_next_tag()

        if event.key == "b":
            self.reset_lims()
            self.show_previous_tag()

        if event.key == "t":
            name = type(self.selector).__name__
            if self.selector.active:
                print(f'{name} deactivated.')
                self.selector.set_active(False)
            else:
                print(f'{name} activated.')
                self.selector.set_active(True)

            return

        self.figure.canvas.draw_idle()

    def save_tag_to_database(self, tag):
        try:
            db = pd.read_csv(self.tag_db_path)
        except FileNotFoundError:
            db = pd.DataFrame()

        db = pd.concat([db, tag.to_frame().T], ignore_index=True)
        db.id = db.id.astype(int).astype(str)
        
        # remove duplicates
        db = self.remove_duplicates(db)
        db.sort_values(by=["image_hash", "id"], ascending=True)

        # save tagged image to folder according to a unique identifier
        self.save_tag_image_to_database(tag)
        
        # save updated database
        db.to_csv(self.tag_db_path, index=False)

    def save_tag_image_to_database(self, tag):
        """
        convenience to start creating a ML databse for organisms
        all tags could be reproduced 
        """
        filename = os.path.join(
            os.path.dirname(self.tag_db_path), 
            "annotated_images", 
             f"{tag.image_hash}_tag_{int(tag.id)}.jpg")

        if not os.path.exists(os.path.dirname(filename)):
            os.mkdir(os.path.dirname(filename))

        imageio.imwrite(filename, self.image.pixels[self.ctag.slice])


    @staticmethod
    def remove_duplicates(df):
        """
        id          refers to tag id (running number 1-N)
        img_id      id of image (1-Nsamples)
        img_date    date at which image was taken (Ymd)
        img_time    time at which image was taken (HMS)
        """
        duplicates = df.duplicated(subset=["id","image_hash"], 
                                   keep="last")
        return df.loc[~duplicates, :].copy()
        



    def drop_duplicates(self):
        drop_id = self.ctag.id
        try:
            self.tags = self.tags.drop(drop_id)
        except IndexError:
            pass

    def read_new_tags(self, tags):
        new_tags = tags.export_annotations()
        try:
            new_tags.id
        except AttributeError:
            new_tags['id'] = range(len(new_tags))
        try:
            len(new_tags.label)
        except AttributeError:
            new_tags['label'] = "?"
        try:
            new_tags.analysis
        except AttributeError:
            new_tags['analysis'] = self.analysis
        try:
            new_tags.img_path
        except AttributeError:
            new_tags['img_path'] = self.image.path

        self.save_new_tags(new_tags)

    def reset_lims(self):
        if self.display_whole_img:
            self.ax_complete_fig.set_xlim(self.origx)
            self.ax_complete_fig.set_ylim(self.origy)

    def show_original(self):
        self.ax_complete_fig.imshow(self.image.img)
        self.selector = self.create_selector()
        # initiate as inactive. Has to be activate with "t"
        self.selector.set_active(False)

    def show_sliders(self):
        for ax, par in zip(self.axes_slider, self._slider_parameters):
            slider = self.create_slider(ax, par)
            callback = self.slider_callback(self, par)
            slider.on_changed(callback)
            self.sliders.update({par: [slider, callback]})

    def create_selector(self):
        return RectangleSelector(
            self.ax_complete_fig, self.select_callback,
            useblit=True,
            button=[1],  # disable middle and right button
            minspanx=5, minspany=5,
            spancoords='pixels',
            interactive=True)

    def create_slider(self, ax, detector_parameter):
        par = getattr(self.detector, detector_parameter)
        return Slider(
            ax=ax,
            label=detector_parameter.replace("_", " "),
            valstep=par.step,
            valmin=par.min,
            valmax=par.max,
            valinit=par,
        )


    def show_tagged(self):
        tagged = self.image.tag_image(self.image.img, self.new_tags['contour'])
        self.ax_complete_fig.imshow(tagged)

    def show_label(self):
        try:
            self.axes_tag[0].annotate(self.ctag.label, (0.05,0.05), xycoords="axes fraction",
                                  bbox={'color':'white','ec':'black', 'lw':1},
                                  ha="left", va="bottom")
            self.axes_tag[0].annotate(self.ctag.id, (0.05,0.95), xycoords="axes fraction",
                                  bbox={'color':'white','ec':'black', 'lw':1},
                                  ha="left", va="top")

            pred = f"{self.ctag.pred} ({np.round(self.ctag.prob * 100, 2)} %)"
            self.axes_tag[0].annotate(pred, (0.95,0.95), 
                                xycoords="axes fraction",
                                bbox={'color':'white','ec':'black', 'lw':1},
                                ha="right", va="top")
        except KeyError:
            pass


    def show_tag(self):
        # plot original image
        try:
            self.axes_tag[0].cla()
            # img = self.draw_contour_on_slice()
            s = self.image.pixels[self.ctag.slice]
            if len(s) > 0:
                self.axes_tag[0].imshow(s)
        except KeyError:
            pass

        try:
            self.axes_tag[1].cla()
            self.axes_tag[1].imshow(self.ctag.threshold_img)
        except KeyError:
            pass

        for i, attr in enumerate(self._extra_images):
        # for i, (attr, _) in zip(range(2, 10), extra_objects.items()):
            try:
                self.axes_tag[i+2].cla()
                s = getattr(self.image, attr)[self.ctag.slice]
                if len(s) > 0:
                    self.axes_tag[i+2].imshow(s)
            except KeyError:
                pass

        self.show_label()
        self.set_plot_titles()

    # def draw_contour_on_slice(self):
    #     origin = np.array([[[self.ctag.x, self.ctag.y]]])
    #     ym = self.ctag.tag_image_orig.shape[0] - self.ctag.height
    #     xm = self.ctag.tag_image_orig.shape[1] - self.ctag.width
    #     margins = np.array([xm, ym]) / 2
    #     cnt = self.ctag.tag_contour - origin + margins
    #     cnt = cnt.astype(int)
    #     return cv.drawContours(self.ctag.tag_image_orig, [cnt], 0, (0,255,0), 1)

    def save_new_tags(self, new_tags):
        if len(self.tags) != 0:
            if self._continue_annotation:
                return

            overwrite = input("WARNING! Annotations will be overwritten. Do you want to overwrite? (y/n):")
            if not overwrite == "y":
                return
            else:
                self.tags = pd.DataFrame({'id':[]})
        
        N = len(new_tags)
        tags = []
        with tqdm.tqdm(total=N, desc="reading") as bar:

            for i in range(N):
                t = self.read_tag(new_tags, i)
                t.unpack_dictionaries()
                t.image_hash = self.image_hash
                t = t.save()
                tags.append(t.to_frame().T)

                bar.update(1)

        self.tags = pd.concat(tags, ignore_index=True)        
        self.save_progress()

    def draw_tag_boxes(self):
        patches = []
        for i in self.tags.id:
            tag = self.read_tag(self.tags, i)
            rect = Rectangle((tag.x, tag.y),tag.width,tag.height)

            patches.append(rect)
        
        self._pc = PatchCollection(patches, facecolor="none", edgecolor="green")
        _ = self.ax_complete_fig.add_collection(self._pc)

    def draw_target(self):
        for t in self.target:
            t.remove()

        y = self.ctag.ycenter
        x = self.ctag.xcenter

        v = self.ax_complete_fig.vlines(x, y-50, y+50, color="red")
        h = self.ax_complete_fig.hlines(y, x-50, x+50, color="red")
        self.target = (v, h)

    def read_tag(self, tags, tag_id):
        t = Tag(props=tags.loc[tag_id, :])
        return t
        # self.new_tags = self.new_tags.drop(i)

    def get_tag_number_from_id(self, tag_id):
        return np.where(self.tags.id.values == tag_id)[0][0]

    def show_tag_number(self, i):
        self.i = i
        tag_id = self.tags.id.values[self.i]
        t = self.read_tag(self.tags, tag_id=tag_id)

        self.ctag = t
        if self.display_whole_img:
            # self.draw_tag_box()
            self.draw_target()
        self.show_tag()

    def show_next_tag(self):
        self.i += 1
        if self.i >= len(self.tags):
            self.i = 0
        self.show_tag_number(i=self.i)

    def show_previous_tag(self):
        self.i -= 1
        if self.i < 0:
            self.i = len(self.tags) - 1

        self.show_tag_number(i=self.i)

    def save_progress(self):
        self._tags.to_csv(self.path, index=False)


class Spectral:
    @staticmethod
    def mask_from_top(mask):
        d = np.flipud(np.flipud(mask).cumsum(axis=0))
        masktop = np.where(d == 0, 0, 255).astype('uint8')

        return masktop

    @staticmethod
    def mask_from_bottom(mask):
        d = np.flipud(np.flipud(mask).cumsum(axis=0))
        masktop = np.where(d > 0, 0, 255).astype('uint8')

        return masktop

    @staticmethod
    def min_filter(n, img):
        size = (n, n)
        shape = cv.MORPH_RECT
        kernel = cv.getStructuringElement(shape, size)

        # Applies the minimum filter with kernel NxN
        return cv.erode(img, kernel)

    @staticmethod
    def max_filter(n, img):
        size = (n, n)
        shape = cv.MORPH_RECT
        kernel = cv.getStructuringElement(shape, size)

        return cv.dilate(img, kernel)

    @classmethod
    def mrm(cls, img, min_kernel_n, range_threshold, max_kernel_n):
        """
        mrm - minimum filter followed by a range threshold and followed by a 
        maximum filter. Is a sequence of image processing steps creates a mask.
        This mask filters a bright and relatively homogeneous feature of an image 
        which has a strong contrast to the surrounding.

        xxx_kernel_n    stands for the kernel size of the respective minimum or 
                        maximum functions. The kernel takes the minimum or maximum
                        respectively for the N x N sized matrix of the kernel
        
        range_threshold transforms the continuous image to a mask consisting of 
                        0 or 255 values. Takes a tuple like object and needs a 
                        min and max threshold like: (20, 255). See cv.inRange()
        """
        img = cls.min_filter(min_kernel_n, img)
        mask = cv.inRange(img, range_threshold[0], range_threshold[1]) # red mask
        mask = cls.max_filter(max_kernel_n, mask)

        return mask

    @staticmethod
    def detect_vertical_peaks(img, return_prop="ips", **peak_args):
        """
        Goes through an image by vertical slices and returns the first peak
        encountered. Peak arguments can pe provided by keywords. Refer to
        scipy.signal find_peaks method to know what arguments can be used. 
        Well working are height and width. Particularly the width argument is 
        important to ensure that only strong enough signals are detected.
        """
        y, x = img.shape
        
        left = [0]
        right = [y]
        
        for i in range(x):
            vline = img[:,i]
            peak_x, props = find_peaks(vline, **peak_args)
            try:
                if len(peak_x) > 1:
                    print(i, "more than one peak")
                left.append(props['left_'+return_prop][0])
                right.append(props['right_'+return_prop][0])
            except IndexError:
                left.append(left[i-1])
                right.append(right[i-1])

        return left[1:], right[1:]

    @staticmethod
    def detect_vertical_extrema(img, smooth_n=10, derivative=1):
        """
        finds extrema in spectral vertical lines of an image. At the moment optimized for
        first derivative. 
        Basically the function looks for an increase first and takes the beginning of 
        the increase and then looks for the decrease of a value again.
        Since the water surface behaves in pretty much this fashion, it works ok
        Wait for problematic images

        Interpolation could help a lot in these cases.
        """
        y, x = img.shape
        
        left = [0]
        right = [y]

        for i in range(x):
            vline = img[:,i]
            if smooth_n > 0:
                vline = gaussian_filter1d(vline, smooth_n)
            
            vline = np.gradient(vline, derivative)
            ex1 = argrelextrema(vline, np.less)[0]
            ex2 = argrelextrema(vline, np.greater)[0]
            try:
                left.append(ex1[0])
            except IndexError:
                print("not enough peaks.")
                left.append(left[i-1])

            try:
                right.append(ex2[1])
            except IndexError:
                print("not enough peaks.")
                right.append(right[i-1])


        return left[1:], right[1:]

    @staticmethod
    def extend_horiz_border(border, img, towards="bottom", smooth_n=0, 
                            y_offset=(0,0), fill=0):
        
        """
        The method takes a 1D array or list as an input as well as an image. Both
        must have the same x dimension (eg. if the border is of len 10, the image 
        must by Y x 10 as well. It returns an image which is filled from the 
        border until top or bottom or until a second border). 
        
        border      1D array of same x-dimension as img
        img         2D array
        smooth_n    if set to value greater 1, the array is smoothed beforehand
        y_offset    array like of len=2, specifies if the border is offset and the
                    second interval is offset as well
        fill        is the number with whihc the array is filled
        """
        y, x = img.shape
        
        if smooth_n > 0:
            a = np.round(gaussian_filter1d(border, smooth_n)).astype('int')
        else:
            a = np.round(border).astype('int')

        a = a + y_offset[0]
        
        assert len(a) == x, "img and border should have the same x dimension"
        
        if isinstance(towards, (np.ndarray, list)):
            if smooth_n > 0:
                b = np.round(gaussian_filter1d(towards, smooth_n)).astype('int')
            else:
                b = np.round(towards).astype('int')
            
            b = b + y_offset[1]
            assert len(a) == len(b)
        elif towards == "bottom":
            b = np.repeat(y+y_offset[1], x)
        elif towards == "top":
            b = a
            a = np.repeat(0+y_offset[1], x)


        # im sure for this exists a numpy method        
        for i in range(x):
            img[a[i]:b[i], i] = fill

        return img.astype('uint8')

        
class Preprocessing:
    """
    contains method which perform single or sequential proceedures on images
    either returning the image itself, or a list of images
    """
    @staticmethod
    def intersection(img, maxval=255):
        intersec = ( img[:,:,0] * img[:,:,1] 
                   + img[:,:,0] * img[:,:,2] 
                   + img[:,:,2] * img[:,:,1] )
        return np.where(intersec >= maxval, 255, 0).astype('uint8')

    @staticmethod
    def substract_median(img, ignore_value=None):
        im = img.copy().astype('int')
        assert len(img.shape) >= 2, "img must be 2D and have at least one color channel"

        if len(img.shape) == 2:
            im[:,:] = im[:,:] - np.median(im[:,:].flatten())
            
        elif len(img.shape) == 3:
            y, x, colors = img.shape

            for c in range(colors):
                data = im[:,:,c].flatten()
                if ignore_value is not None:
                    data = np.ma.masked_where(data == ignore_value, data).compressed()
                im[:,:,c] = im[:,:,c] - np.median(data)

        return np.where(im > 0, im, 0).astype('uint8')

    @staticmethod
    def canny_edge_detection(
        img, blur=None, max_filter_kernel_width=None,
        min_filter_kernel_width=None, resize=None, canny_thresholds=None):
        steps = [img]
        steps.append(cv.resize(steps[-1], (0, 0), fx=resize, fy=resize))
        steps.append(cv.medianBlur(steps[-1], blur))
        steps.append(Spectral.max_filter(max_filter_kernel_width, steps[-1]))
        steps.append(cv.Canny(steps[-1], canny_thresholds[0], canny_thresholds[1]))
        # kernel = cv.getStructuringElement(cv.MORPH_ELLIPSE,(9,9))
        # steps.append(cv.dilate(steps[-1], kernel))
        return steps

    @classmethod
    def median_threshold(cls, roi, blur, threshold, ignore_value):
        median = cv.medianBlur(roi, blur)
        background = cls.substract_median(median, ignore_value)
        gray = cv.cvtColor(background, cv.COLOR_RGB2GRAY)
        T, thresh = cv.threshold(gray, threshold, 255, 0)
        return [roi, thresh]

    @classmethod
    def threshold_and_morphology(cls, img,
        smooth_input=1, lag_between_images=1, color_threshold=20, 
        morphology_kernel=20, min_filter_size=1):

        ret, thresh = cv.threshold(img, color_threshold, 255,0)

        # get intersection of thresholded values
        intersec = cls.intersection(thresh, 1)

        # combine elements
        k = cv.getStructuringElement(
            cv.MORPH_ELLIPSE, ksize=(morphology_kernel, morphology_kernel))
        morph = cv.morphologyEx(intersec, op=cv.MORPH_CLOSE, kernel=k)

        # remove intersections of just 1 pixel (could maybe removed later)
        mini = Spectral.min_filter(min_filter_size, morph)

        return [img, thresh, intersec, morph, mini]