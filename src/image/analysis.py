import pandas as pd
import numpy as np
import cv2
import matplotlib as mpl
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
import sys
import os
from utils.manage import Files
import imageio
import time

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
    def __init__(self, image, analysis):
        self.image = image
        self.analysis = analysis
        self.origx = (0, image.img.shape[1])
        self.origy = (image.img.shape[0],0)
        self.xlim = (0,0)
        self.ylim = (0,0)
        self.tags = pd.DataFrame({'id':[]})
        self.ctag = None
        self.keymap = {
            'd':"Daphnia Magna",
            'c':"Culex Pipiens, larva",
            'p':"Culex Pipiens, pupa",
            'u':"unidentified",
        }
        
        fname = '_'+analysis+'_tags.csv'
        self.path = self.image.append_to_filename(self.image.path, fname)
        



    def start(self):
        # create figure
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
        self.tags = pd.read_csv(self.path)



    def press(self, event):
        print('press', event.key)
        sys.stdout.flush()
        if event.key in self.keymap.keys():
            self.ctag.label = self.keymap[event.key]
            self.ctag.annotated = True
            t, p = self.ctag.save()
            self.drop_duplicates()
            self.tags = self.tags.append(t, ignore_index=True)
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
    def __init__(self, path):
        self.path = path

    @staticmethod
    def collect_annotations(path, search_keyword):
        files = Files.search_files(path, search_keyword)
        df = DataFrame()

        for f in files:
            d = Files.read(f)
            df.append(f, inplace=True)
        return df

    def collect_id(self, path, search_keyword):
        s = Series(path, import_image=False)

        for p in pics:
            d = self.collect_annotations(path, search_keyword)
            
            if add_id_col:
                d['nano_id'] = p
            
            df.append(d)

        return df

    def collect_session(self):
        pass

    def collect_all(self):
        pass




