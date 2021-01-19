import os
import sys
import time
import cv2
import shutil
import imageio
import pandas as pd
import numpy as np
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from utils.manage import Files
from image.process import Image
from icecream import ic

class Tag(Files):
    def __init__(self):
        # tag attributes which are saved to df
        self.id = 0
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0
        self.label = ""
        self.time = ''
        self.analysis = 'none'
        self.annotated = False

        # temporary attributes
        self.path = ""
        
        # special attributes with custom save methods
        self.tag_contour = np.array([])
        self.tag_image_orig = np.array([])
        self.tag_image_diff = np.array([])

    def load_special(self):
        path = self.change_dir(self.analysis)
        specials = self.find_subdirs(path)

        for attr in specials:
            ext = os.listdir(os.path.join(path, attr))[0].split('.')[1]
            value = Files.read(os.path.join(path, attr, str(int(self.id))+'.'+ext))
            setattr(self, attr, value)

    def save(self):
        """
        removes all attributes from tag which are not needed, or are unsuitable
        for dataframes (those are saved in arrays or tiffs).
        The remainder is forwarded to a dataframe, which can easily be 
        """
        self.time = time.strftime('%Y-%m-%d %H:%M:%S')
        tag = self.__dict__.copy()
        p = self.create_dir(self.analysis)

        # save_tag_slice
        img_orig = tag.pop('tag_image_orig')
        p = self.create_dir(os.path.join(self.analysis, 'tag_image_orig'))
        imageio.imwrite(os.path.join(p, str(int(self.id))+'.tiff'), img_orig)

        # save tag slice from diff pic (maybe not necessary)
        img_diff = tag.pop('tag_image_diff')
        p = self.create_dir(os.path.join(self.analysis, 'tag_image_diff'))
        imageio.imwrite(os.path.join(p, str(int(self.id))+'.tiff'), img_diff)

        # save contour
        contour = tag.pop('tag_contour')
        p = self.create_dir(os.path.join(self.analysis, 'tag_contour'))
        np.save(os.path.join(p, str(int(self.id))+'.npy'), contour)

        p = tag.pop("path")
        return pd.Series(tag), p

    def get_tag_box_coordinates(self):
        x = self.x
        y = self.y
        w = self.width
        h = self.height

        if x + y + w + h == 0:
            x, y, w, h = cv2.boundingRect(self.tag_contour)
            self.x = x
            self.y = y
            self.width = w
            self.height = h

        return x, y, w, h

# interactive figure
class Annotations(Tag): 
    def __init__(self, image, analysis, tag_db_path, keymap={}):
        self.image = image
        self.tag_db_path = tag_db_path
        self.analysis = analysis
        self.origx = (0,0)
        self.origy = (0,0)
        self.xlim = (0,0)
        self.ylim = (0,0)
        self.tags = pd.DataFrame({'id':[]})
        self.ctag = None
        self.error = (False, "no message")
        self.keymap = keymap
        
        fname = '_'+analysis+'_tags.csv'
        self.path = self.image.append_to_filename(self.image.path, fname)
        



    def start(self):
        # create figure
        self.origx = (0, self.image.img.shape[1])
        self.origy = (self.image.img.shape[0],0)
        self.gs = plt.GridSpec(nrows=2, ncols=2)
        self.figure = plt.figure()
        self.figure.canvas.mpl_connect('key_press_event', self.press) 
        mpl.rcParams['keymap.back']:['left'] 
        mpl.rcParams['keymap.pan']:[] 
        mpl.rcParams['keymap.pan']:[] 
        self.axes = {}

        self.axes[0] = plt.subplot(self.gs[0:2, 0])
        self.axes[1] = plt.subplot(self.gs[0, 1])
        self.axes[2] = plt.subplot(self.gs[1, 1])

        self.show_original()
        plt.ion()


    def load_processed_tags(self):
        try:
            self.tags = pd.read_csv(self.path)
        except FileNotFoundError:
            self.error = (True, self.path)



    def press(self, event):
        print('press', event.key)
        sys.stdout.flush()
        if event.key in self.keymap.keys():
            self.ctag.label = self.keymap[event.key]
            self.ctag.annotated = True
            t, p = self.ctag.save()
            self.drop_duplicates()
            self.tags = self.tags.append(t, ignore_index=True)
            self.save_tag_to_database(t, add_attrs=['id','date','time'])
            self.show_label()

        if event.key == "n":
            self.reset_lims()
            self.show_next_tag()

        if event.key == "b":
            self.reset_lims()
            self.show_previous_tag()

        self.figure.canvas.draw()
        self.tags = self.tags.sort_values(by='id')
        self.save_progress()

    def save_tag_to_database(self, tag, add_attrs=[]):
        db = pd.read_csv(self.tag_db_path)
        for a in add_attrs:
            tag['img_'+a] = getattr(self.image, a)
        db = db.append(tag, ignore_index=True)
        db.to_csv(self.tag_db_path, index=False)
        

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

        self.save_new_tags(new_tags)

    def reset_lims(self):
        self.axes[0].set_xlim(self.origx)
        self.axes[0].set_ylim(self.origy)

    def show_original(self):
        self.axes[0].imshow(self.image.img)

    def show_tagged(self):
        tagged = self.image.tag_image(self.image.img, self.new_tags['contour'])
        self.axes[0].imshow(tagged)

    def show_label(self):
        self.axes[1].annotate(self.ctag.label, (0.05,0.05), xycoords="axes fraction",
                        bbox={'color':'white','ec':'black', 'lw':2})

    def show_tag(self):
        self.axes[1].cla()
        self.axes[1].imshow(self.ctag.tag_image_orig)
        self.axes[2].cla()
        self.axes[2].imshow(self.ctag.tag_image_diff)
        self.show_label()

    def save_new_tags(self, new_tags):
        for i in range(len(new_tags)):
            t = self.read_tag(new_tags, i)
            t.get_tag_box_coordinates()
            t, p = t.save()
            self.tags = self.tags.append(t, ignore_index=True)
        
        self.save_progress()

    def draw_tag_box(self):
        x, y, w, h = self.ctag.get_tag_box_coordinates()

        rect = Rectangle((x,y),w,h, linewidth=5, fill=False, color="red")
        # [ptch.remove() for ptch in reversed(self.axes[0].patches)]
        for p in reversed(self.axes[0].patches):
            p.set_color('green')
            p.set_linewidth(1)
        self.axes[0].add_patch(rect)

    def read_tag(self, tags, i):
        t = Tag()
        t.path = self.image.path
        t.__dict__.update(tags.iloc[self.get_id(tags, i)[0]])
        return t
        # self.new_tags = self.new_tags.drop(i)

    def show_tag_number(self, i):
        self.i = i
        t = self.read_tag(self.tags, i)
        self.ctag = t
        self.ctag.load_special()
        self.draw_tag_box()
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
        self, path, search_keyword, import_images=False,
        date="all", sample_id="all", img_num="all",
        correct_path=(False,0,"")
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


    def collect(self):
        paths = self.collect_paths(self.path, date=self.date, sample_id=self.id, img_num=self.img_num)
        self.images = self.collect_files(paths, self.keyword, self.import_images, self.correct_path)
        self.data = self.extract_data(self.images, self.attrs)
        self.check_for_errors()
        self.data = self.rename_columns(self.data, self.index_names, 'tag')

        self.index()
        self.order()

    def index(self):
        tstamp = pd.to_datetime(self.data.img_date+self.data.img_time, format='%Y%m%d%H%M%S').to_numpy()
        tag_id = self.data.tag_id.to_numpy(dtype=int)
        img_id = self.data.img_id.to_numpy(dtype=int)
        idx = pd.MultiIndex.from_arrays([tstamp, img_id, tag_id], names=self.index_names)

        self.data.index = idx
        self.data = self.data.drop(columns=['img_date','img_time','tag_id','img_id'])

    def order(self):
        self.data = self.data.sort_values(by = self.index_names)

    def check_for_errors(self):
        errors = [i.tags.error[1] for i in self.images if i.tags.error[0]]
        if len(errors) > 0:
            self.errors = errors
            print("Warning: Errors during file import -> for details see obj.errors")

    @classmethod
    def extract_data(cls, images, attrs=['id', 'date', 'time']):
        df = pd.DataFrame()
        for i in images:
            idata = cls.label_data(i, attrs)
            df = df.append(idata)
        
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
    def collect_files(paths, search_keyword, 
                      import_images=False, 
                      correct_path=(False, 0, '')):
        images = []
        for p in paths:
            i = Image(p)
            i.read_struct(import_image=import_images)
            if correct_path[0]:
                i.path = Files.change_top_dirs(i.path, strip_levels=correct_path[1], add_path=correct_path[2])
            i.tags = Annotations(image=i, analysis=search_keyword, tag_db_path="")
            i.tags.load_processed_tags()

            images.append(i)

        return images

