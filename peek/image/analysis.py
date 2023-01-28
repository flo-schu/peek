import os
import sys
import time
import shutil
import imageio
import warnings
import cv2 as cv
import pandas as pd
import numpy as np
import tqdm
import matplotlib as mpl
from glob import glob
from datetime import datetime
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import PatchCollection
from matplotlib.widgets import RectangleSelector
from scipy.ndimage import gaussian_filter1d
from scipy.signal import argrelextrema, find_peaks

from toopy.pandas import read_csv_list

from peek.utils.manage import Files
from peek.image.process import Snapshot



class Tag(Files):
    def __init__(self):
        # tag attributes which are saved to df
        # IF POSSIBLE NEVER CHANGE THESE NAMES. WHY?
        # THEN THE DATA WILL BE HOMOGENEOUSLY NAMED ACCROSS ALL ANALYSES
        # ----------------------------------------------------------------------
        self.image_hash = None      # unique reference hash of parent image
        self.id = 0                 # id of tag in image
        self.x = 0                  # top left corner of bounding box (x-axis)
        self.y = 0                  # top left corner of bounding box (y-axis)
        self.width = 0              # width of bounding box
        self.height = 0             # height of bounding box
        self.label = ""             # label of manual classification
        self.time = ''              # time of detection
        self.analysis = 'none'      # name of analysis 
        self.annotated = False      # was the label manually annotated
        self.xcenter = 0            # x-coordinate of center of detected object
        self.ycenter = 0            # y-coordinate of center of detected object
        # ----------------------------------------------------------------------
        
        # temporary attributes
        self.path = ""
        
        # special attributes with custom save methods
        self.tag_contour = np.array([])
        self.tag_image_orig = np.array([])
        self.tag_image_diff = np.array([])
    
    def unpack_dictionaries(self):
        pop_dicts = []
        for key, item in self.__dict__.items():
            if isinstance(item, dict):
                pop_dicts.append(key)
        
        for d in pop_dicts:
            for key, value in self.__dict__.pop(d).items():
                setattr(self, key, value)

    def load_special(self):
        path, ext = os.path.splitext(self.path)
        specials = os.listdir(path)

        for attr in specials:
            subdir = os.path.join(path, attr)
            if os.path.isdir(subdir):
                ext = os.listdir(subdir)[0].split('.')[1]
                value = Files.read(os.path.join(path, attr, str(int(self.id))+'.'+ext))
                setattr(self, attr, value)

    def save(self, store=True):
        """
        removes all attributes from tag which are not needed, or are unsuitable
        for dataframes (those are saved in arrays or tiffs).
        The remainder is forwarded to a dataframe, which can easily be 
        """
        self.time = time.strftime('%Y-%m-%d %H:%M:%S')
        tag = self.__dict__.copy()
        if store:
            path, ext = os.path.splitext(self.path)
            if not os.path.exists(path):
                os.mkdir(path)

        # save_tag_slice
        img_orig = tag.pop('tag_image_orig')
        if store:
            if img_orig.size > 0:
                p_ = os.path.join(path, 'tag_image_orig')
                os.makedirs(p_, exist_ok=True)
                imageio.imwrite(os.path.join(p_, str(int(self.id))+'.jpg'), img_orig)

        # save tag slice from diff pic (maybe not necessary)
        img_diff = tag.pop('tag_image_diff')
        if store:
            if img_diff.size > 0:
                p_ = os.path.join(path, 'tag_image_diff')
                os.makedirs(p_, exist_ok=True)
                imageio.imwrite(os.path.join(p_, str(int(self.id))+'.jpg'), img_diff)

        # save contour
        contour = tag.pop('tag_contour')
        if store:
            if contour.size > 0:
                p_ = os.path.join(path, 'tag_contour')
                os.makedirs(p_, exist_ok=True)
                np.save(os.path.join(p_, str(int(self.id))+'.npy'), contour)

        path = tag.pop("path")
        return pd.Series(tag), path

    def get_tag_box_coordinates(self):
        x = self.x
        y = self.y
        w = self.width
        h = self.height

        if x + y + w + h == 0:
            x, y, w, h = cv.boundingRect(self.tag_contour)
            self.x = x
            self.y = y
            self.width = w
            self.height = h

        return x, y, w, h

# interactive figure
class Annotations(Tag): 
    def __init__(
        self, 
        path,
        image=None, 
        image_metadata={},
        analysis="undefined", 
        tag_db_path="annotations/tag_db.csv", 
        keymap={
            'd':"Daphnia Magna",
            'c':"Culex Pipiens, larva",
            'p':"Culex Pipiens, pupa",
            'u':"unidentified"
            },
        store_extra_files = True,
        zfill=0,
        ):
        self.path = os.path.normpath(path)
        self.analysis = analysis
        self.tags = self.load_processed_tags()
        self.image = self.load_image(image, image_metadata)
        self.image_hash = self.image.__hash__()
        self.store_extra_files = store_extra_files
        self.display_whole_img = False
        self.tag_db_path = tag_db_path
        self.origx = (0,0)
        self.origy = (0,0)
        self.xlim = (0,0)
        self.ylim = (0,0)
        self.ctag = None
        self.error = (False, "no message")
        self.keymap = keymap
        self.zfill = zfill
        self.target = ()
        self.seletctor = None
        self._pc = None

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
        self.figure = plt.figure()
        self.figure.canvas.mpl_connect('key_press_event', self.press) 
        mpl.rcParams['keymap.back'] = ['left'] 
        mpl.rcParams['keymap.pan'] = [] 
        mpl.rcParams['keymap.pan'] = [] 
        
        # create figure
        init_plot = getattr(self, plot_type)
        self.axes = {}
        init_plot()
        self.set_plot_titles()

        plt.ion()
        self.draw_tag_boxes()
        self.show_tag_number(0)
        plt.show()


    # def test(self, eclick=(1750, 800), erelease=(1770, 810)):
    def select_callback(self, eclick, erelease):
        """
        Callback for line selection.

        *eclick* and *erelease* are the press and release events.
        """
        x1, y1 = int(eclick.xdata), int(eclick.ydata)
        x2, y2 = int(erelease.xdata), int(erelease.ydata)
        t = Tag()
        t.path = self.path
        t.image_hash = self.image_hash
        t.img_path = self.image.path
        t.id = len(self.tags)
        t.x = x1
        t.y = y1
        t.width = x2 - x1
        t.height = y2 - y1
        t.label = "?"
        t.time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        t.analysis = self.analysis
        t.annotated = False
        t.xcenter = (x1 + x2) / 2
        t.ycenter = (y1 + y2) / 2
        t.tag_contour = np.array([[[x1, y1]], [[x2, y2]]])
        t.tag_image_orig = self.image.slice_image(
            self.image.pixels, *cv.boundingRect(t.tag_contour), mar=0)
        t.tag_image_diff = t.tag_image_orig
        new_tag, _ = t.save()

        print(f"created new tag {t}")

        self.tags = pd.concat([self.tags, new_tag.to_frame().T], ignore_index=True)
        self._pc.remove()
        self.draw_tag_boxes()
        self.save_progress()


    def plot_complete_tag_diff(self):
        self.display_whole_img = True
        self.origx = (0, self.image.img.size[0])
        self.origy = (self.image.img.size[1],0)
        self.gs = plt.GridSpec(nrows=2, ncols=2)

        self.axes[0] = self.figure.add_subplot(self.gs[0:2, 0])
        self.axes[1] = self.figure.add_subplot(self.gs[0, 1])
        self.axes[2] = self.figure.add_subplot(self.gs[1, 1])
        self.show_original()

    def plot_tag(self):
        self.axes = {
            1: self.figure.add_subplot(111)
        }

    def plot_tag_diff(self):
        self.axes = {
            1: self.figure.add_subplot(121),
            2: self.figure.add_subplot(122),
        }

    def set_plot_titles(self):
        titles = {
            0: "original image",
            1: "tag original",
            2: "tag diff"
        }

        for key, ax in self.axes.items():
            ax.set_title(titles[key])
        
    def load_processed_tags(self):
        try:
            tags = pd.read_csv(self.path)
            analysis = tags.analysis.unique()
            assert len(analysis) == 1, f"multiple analyses in .csv file {analysis}"
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


    def press(self, event):
        print('press', event.key)
        sys.stdout.flush()
        if event.key in self.keymap.keys():
            self.ctag.label = self.keymap[event.key]
            self.ctag.annotated = True
            t, p = self.ctag.save()
            self.drop_duplicates()
            self.tags = pd.concat([self.tags, t.to_frame().T], ignore_index=True)
            self.save_tag_to_database(t)
            self.show_label()

            self.tags = self.tags.sort_values(by='id')
            self.save_progress()

            # directly go to next tag after labeling
            self.reset_lims()
            self.show_next_tag()

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

        self.figure.canvas.draw()

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
        self.copy_tag_image(tag)
        
        # save updated database
        db.to_csv(self.tag_db_path, index=False)

    def copy_tag_image(self, tag):
        path, _ = os.path.splitext(self.path) 
        from_path = os.path.join(
            path,
            "tag_image_orig",
            str(int(tag.id)) + ".jpg"
        )

        to_path = os.path.join(
            os.path.dirname(self.tag_db_path), 
            "annotated_images", 
             f"{tag.image_hash}_tag_{int(tag.id)}.jpg")

        os.makedirs(os.path.dirname(to_path), exist_ok=True)
        shutil.copy(from_path, to_path)

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
        

    @staticmethod
    def get_id(tags, tag_id):
        return tags[tags['id']==tag_id].index

    def drop_duplicates(self):
        drop_id = self.get_id(self.tags, self.ctag.id)
        try:
            self.tags = self.tags.drop(drop_id)
        except IndexError:
            pass

    def read_new_tags(self, new_tags):
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
            self.axes[0].set_xlim(self.origx)
            self.axes[0].set_ylim(self.origy)

    def show_original(self):
        self.axes[0].imshow(self.image.img)
        self.selector = self.create_selector()

    def create_selector(self):
        return RectangleSelector(
            self.axes[0], self.select_callback,
            useblit=True,
            button=[1, 3],  # disable middle button
            minspanx=5, minspany=5,
            spancoords='pixels',
            interactive=True)

    def show_tagged(self):
        tagged = self.image.tag_image(self.image.img, self.new_tags['contour'])
        self.axes[0].imshow(tagged)

    def show_label(self):
        try:
            self.axes[1].annotate(self.ctag.label, (0.05,0.05), xycoords="axes fraction",
                                  bbox={'color':'white','ec':'black', 'lw':2})
            self.axes[1].annotate(self.ctag.id, (0.05,0.95), xycoords="axes fraction",
                                  bbox={'color':'white','ec':'black', 'lw':2})
        except KeyError:
            pass

    def show_tag(self):
        try:
            self.axes[1].cla()
            self.axes[1].imshow(self.ctag.tag_image_orig)
        except KeyError:
            pass
        try:
            self.axes[2].cla()
            self.axes[2].imshow(self.ctag.tag_image_diff)
        except KeyError:
            pass

        self.show_label()
        self.set_plot_titles()

    def save_new_tags(self, new_tags):
        if len(self.tags) != 0:
            warnings.warn("overwriting existing annotations")
            self.tags = pd.DataFrame({'id':[]})
        
        print("reading tags...")
        N = len(new_tags)
        tags = []
        with tqdm.tqdm(total=N) as bar:

            for i in range(N):
                t = self.read_tag(new_tags, i)
                t.unpack_dictionaries()
                t.get_tag_box_coordinates()
                t.image_hash = self.image_hash
                t, _ = t.save(self.store_extra_files)
                tags.append(t.to_frame().T)

                bar.update(1)

        self.tags = pd.concat(tags, ignore_index=True)        
        self.save_progress()

    def draw_tag_boxes(self):
        patches = []
        for i in range(len(self.tags)):
            tag = self.read_tag(self.tags, i)
            x, y, w, h = tag.get_tag_box_coordinates()
            rect = Rectangle((x,y),w,h)

            patches.append(rect)
        
        self._pc = PatchCollection(patches, facecolor="none", edgecolor="green")
        _ = self.axes[0].add_collection(self._pc)

    def draw_tag_box(self):
        x, y, w, h = self.ctag.get_tag_box_coordinates()
        
        rect = Rectangle((x,y),w,h, linewidth=5, fill=False, color="red")
        # [ptch.remove() for ptch in reversed(self.axes[0].patches)]
        for p in reversed(self.axes[0].patches):
            p.set_color('green')
            p.set_linewidth(1)
        self.axes[0].add_patch(rect)

    def get_center_bbox(self):
        x, y, w, h = self.ctag.get_tag_box_coordinates()
        return x + np.round(w / 2), y + np.round(h / 2)

    def draw_target(self):
        for t in self.target:
            t.remove()

        x, y = self.get_center_bbox()
        v = self.axes[0].vlines(x, y-50, y+50, color="red")
        h = self.axes[0].hlines(y, x-50, x+50, color="red")
        self.target = (v, h)


    def read_tag(self, tags, i):
        t = Tag()
        t.path = self.path
        t.__dict__.update(tags.iloc[self.get_id(tags, i)[0]])
        return t
        # self.new_tags = self.new_tags.drop(i)

    def show_tag_number(self, i):
        self.i = i
        t = self.read_tag(self.tags, i)
        self.ctag = t
        self.ctag.load_special()
        if self.display_whole_img:
            # self.draw_tag_box()
            self.draw_target()
        self.show_tag()

    def show_next_tag(self):
        if self.i + 1 >= len(self.tags):
            self.i = - 1
        self.show_tag_number(self.i + 1)

    def show_previous_tag(self):
        if self.i - 1 < 0:
            self.i = len(self.tags)
        self.show_tag_number(self.i - 1)

    def save_progress(self):
        self.tags.to_csv(self.path, index=False)


class Data:
    """
    Data contains methods for reading files and storing them in specific locations
    if a data instance is initiated, it opens a file where search results are appended
    to.
    """
    def __init__(
        self, path, search_keyword="", import_images=False,
        date="all", sample_id="all", img_num="all",
        correct_path={}
        ):
        self.data=None
        self.path = path
        self.keyword = search_keyword
        self.import_images = import_images
        self.attrs=['id', 'date', 'time']
        self.index_names=['time', 'id', 'object']
        self.correct_path=correct_path

        self.date = date
        self.id = sample_id
        self.img_num = img_num
        self.images = []

    @staticmethod
    def read_meta(globpath):
        """
        convenience function for reading all metafiles from a directory created
        by read_meta.py

        globpath    should be constructed in order to select all csv files 
                    e.g. "data/pics_classic/meta/*meta.csv".
                    See documentation of glob()
        """
        meta = read_csv_list(glob(globpath), 
        kwargs={"dtype":{"time":str,"id":int}})
        meta['picture'] = meta.groupby(["date","id"]).cumcount()
        
        return meta


    def collect(self, sample_id=None, date=None, img_num=None):
        if sample_id is not None:
            self.id = sample_id
        if date is not None:
            self.date = date
        if img_num is not None:
            self.img_num = img_num
        paths = self.collect_paths(self.path, date=self.date, sample_id=self.id, img_num=self.img_num)
        self.images = self.collect_files(paths, self.keyword, self.import_images, self.correct_path)
        self.data = self.extract_data(self.images, self.attrs)
        self.check_for_errors()
        self.data = self.rename_columns(self.data, self.index_names, 'tag')

        self.index_images()
        self.order()

        return self.data

    def index_images(self):
        tstamp = pd.to_datetime(self.data.img_date+self.data.img_time, format='%Y%m%d%H%M%S').to_numpy()
        tag_id = self.data.tag_id.to_numpy(dtype=int)
        img_id = self.data.img_id.to_numpy(dtype=int)
        idx = pd.MultiIndex.from_arrays([tstamp, img_id, tag_id], names=self.index_names)

        self.data.index = idx
        self.data = self.data.drop(columns=['img_date','img_time','tag_id','img_id'])

    # @staticmethod
    # def multi_dt_index(df, dtcols, idxcols, names=[]):
    #     """
    #     creates a mult datetime index from date columns and other id columns
    #     for datetime objects the respective format can be added

    #     df          pandas DataFrame object
    #     dtcols      dict, {"colname": "format"} (format e.g. "%Y-%m-%d")
    #     idxcols     list
    #     """
    #     for column, dt_fmt in dtcols.items():
    #         df[column] = pd.to_datetime(df[column], format=dt_fmt)

    #     # create a flat list of index columns
    #     idx = list(dtcols.keys()) + idxcols
    #     df.rename(columns = )
    #     df.set_index(idx, inplace=True)
    #     df = df.drop

    #     return 

    #     # create datetime

    def order(self):
        self.data = self.data.sort_values(by = self.index_names)

    def check_for_errors(self):
        errors = [i.tags.error[1] for i in self.images if i.tags.error[0]]
        if len(errors) > 0:
            self.errors = errors
            print("Warning: Errors during file import -> for details see obj.errors")

    def connect_other_data(self, df):
        pass

    @classmethod
    def extract_data(cls, images, attrs=['id', 'date', 'time']):
        df = pd.DataFrame()
        for i in images:
            idata = cls.label_data(i, attrs)
            df = df.append(idata)
        
        return df
    
    @staticmethod
    def index_df(df, time_col, time_fmt, other_cols, new_index_names, drop=True):
        tstamp = pd.to_datetime(df[time_col], format=time_fmt).to_numpy()
        idx_cols = [tstamp]
        for i in other_cols:
            idx_cols.append(df[i].to_numpy())
        idx = pd.MultiIndex.from_arrays(idx_cols, names=new_index_names)
        df.index = idx
        if drop:
            df = df.drop(columns=[time_col]+other_cols)

        return df

    @staticmethod
    def rename_columns(df, change_cols, prepend):
        for col in change_cols:
            df = df.rename(columns={col:prepend+'_'+col})

        return df

    @staticmethod
    def label_data(image, attrs=[]):
        idata = image.tags.tags
        for a in attrs:
            idata['img_'+a] = getattr(image, a)
        return idata

    @staticmethod
    def collect_paths(path, date="all", sample_id="all", img_num="all"):
        """
        path            should be top-level path where all sessions are stored
        search_keyword  analysis from which tags should be imported
        date            date from which ids should be collected (YYYYMMDD) or "all"
                        if all dates from one id should be gathered    
        id              look for sepcific id in sessions or "all" (start with 1 for 1st image) 
        """
        sessions = [d for d in Files.find_subdirs(path) if Files.is_date(d)]
        if date != "all":
            sessions = [d for d in sessions if d == date]

        sessions = [os.path.join(path, d) for d in sessions]

        ids = []
        for s in sessions:
            s_ids = Files.find_subdirs(s)
            if sample_id != "all":
                s_ids = [id_ for id_ in s_ids if id_ == str(sample_id)]

            ids.extend([os.path.join(s, id_) for id_ in s_ids])

        image_paths = []

        for id_ in ids:
            id_imgs = Files.find_subdirs(id_)
            if img_num != "all":
                id_imgs = id_imgs[int(img_num)-1:int(img_num)]
            image_paths.extend([os.path.join(id_, img) for img in id_imgs])
            
        return image_paths

    @staticmethod
    def collect_meta(paths):
        meta = []
        for p in paths:
            i = Image(p, import_image=False)
            del i.path
            del i.tags
            del i.img
            del i.analyses
            meta.append(i)

        # create multiindex
        meta = pd.DataFrame([m.__dict__ for m in meta])
        imts = pd.to_datetime(meta.date, format='%Y%m%d').to_numpy()
        imid = meta.id.to_numpy(dtype=int)
        meta.index = pd.MultiIndex.from_arrays([imts, imid], names=["date", "id"])
        meta = meta.drop(columns=["date","id"])
        return meta

    @staticmethod
    def collect_files(paths, search_keyword, 
                      import_images=False, 
                      correct_path={}):
        images = []
        for p in paths:
            i = Image(p)
            i.read_struct(import_image=import_images, ignore_struct_path=False)
            i.path = Files.change_root_of_path(i.path, **correct_path)
            i.tags = Annotations(image=i, analysis=search_keyword, tag_db_path="")
            i.tags.load_processed_tags()

            images.append(i)

        return images


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