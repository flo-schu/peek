import pandas as pd
import cv2
import matplotlib as mpl
from matplotlib import pyplot
from matplotlib.patches import Rectangle
import sys

# interactive figure
class Annotations(): 
    def __init__(self, image):
        self.image = image
        self.origx = (0, image.img.shape[1])
        self.origy = (image.img.shape[0],0)
        self.xlim = (0,0)
        self.ylim = (0,0)
        self.ctag = None
        self.keymap = {
            'd':"Daphnia Magna",
            'c':"Culex Pipiens, larva",
            'p':"Culex Pipiens, pupa",
            'u':"unidentified",
        }

        plt.ion()

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


    def press(self, event):
        print('press', event.key)
        sys.stdout.flush()
        if event.key in self.keymap.keys():
            self.ctag.label = self.keymap[event.key]
            self.tags.iloc[self.i] = self.ctag
            self.show_label()

        if event.key == "n":
            self.reset_lims()
            self.show_next_tag()

        if event.key == "b":
            self.reset_lims()
            self.show_previous_tag()

        self.figure.canvas.draw()
        self.image.save_pkl('tags')

    def label(self):
        pass

    def read_tags(self):
        self.tags = pd.DataFrame(self.image.tags)
        try:
            len(self.tags.label)
        except AttributeError:
            self.tags['label'] = "?"

    def reset_lims(self):
        self.axes[0].set_xlim(self.origx)
        self.axes[0].set_ylim(self.origy)

    def show_original(self):
        self.axes[0].imshow(self.image.img)

    def show_tagged(self):
        tagged = self.image.tag_image(self.image.img, self.tags['contours'])
        self.axes[0].imshow(tagged)

    def show_label(self):
        self.axes[1].annotate(self.ctag["label"], (0.05,0.05), xycoords="axes fraction",
                        bbox={'color':'white','ec':'black', 'lw':2})

    def show_tag(self, tag):
        self.axes[1].cla()
        self.axes[1].imshow(tag["slice_orig"])
        self.axes[2].cla()
        self.axes[2].imshow(tag["slice_comp"])
        self.show_label()


    def draw_tag_box(self):
        x,y,w,h = cv2.boundingRect(self.ctag['contours'])
        rect = Rectangle((x,y),w,h, linewidth=5, fill=False, color="red")
        # [ptch.remove() for ptch in reversed(self.axes[0].patches)]
        for p in reversed(self.axes[0].patches):
            p.set_color('green')
            p.set_linewidth(1)
        self.axes[0].add_patch(rect)

    def show_tag_number(self, i):
        self.i = i
        self.ctag = self.tags.iloc[i]
        self.draw_tag_box()
        self.show_tag(self.ctag)

    def show_next_tag(self):
        self.show_tag_number(self.i + 1)

    def show_previous_tag(self):
        self.show_tag_number(self.i - 1)

    def save_progress(self):
        self.image.save_pkl('tags')