import os
import sys
import time
import shutil
import imageio
import cv2 as cv
import pandas as pd
import numpy as np
import itertools as it
import matplotlib as mpl
from glob import glob
from matplotlib import pyplot as plt
from matplotlib.patches import Rectangle
from scipy.ndimage import gaussian_filter1d
from scipy.signal import argrelextrema, find_peaks

from utils.manage import Files
from image.process import Image, Series

class Tag(Files):
    def __init__(self):
        # tag attributes which are saved to df
        # IF POSSIBLE NEVER CHANGE THESE NAMES. WHY?
        # THEN THE DATA WILL BE HOMOGENEOUSLY NAMED ACCROSS ALL ANALYSES
        # ----------------------------------------------------------------------
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
        image, 
        analysis, 
        tag_db_path, 
        keymap={
            'd':"Daphnia Magna",
            'c':"Culex Pipiens, larva",
            'p':"Culex Pipiens, pupa",
            'u':"unidentified"
            }
        ):
        self.image = image
        self.display_whole_img = False
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
        self.path = self.find_annotations(analysis)

    def find_annotations(self, analysis):
        path = self.image.path

        if path.endswith(".tiff") or os.path.isfile(path):
            fname = '_'+analysis+'_tags.csv'
            path = self.image.append_to_filename(path, fname)
        
        elif os.path.isdir(path):
            tag_file = [f for f in Files.find_files(path, 'tags.csv') if analysis in f]
            print(tag_file)
            assert len(tag_file) == 1, "more than one tag file. something is not right"
            path = os.path.join(path, tag_file[0])
        
        return path
                

    def start(self, plot_type="plot_complete_tag_diff"):
        """
        plot_type   one of "plot_complete_tag_diff", "plot_tag", "plot_tag_diff"
        """
        self.figure = plt.figure()
        self.figure.canvas.mpl_connect('key_press_event', self.press) 
        mpl.rcParams['keymap.back']:['left'] 
        mpl.rcParams['keymap.pan']:[] 
        mpl.rcParams['keymap.pan']:[] 
        
        # create figure
        init_plot = getattr(self, plot_type)
        self.axes = {}
        init_plot()
        self.set_plot_titles()

        plt.ion()
        plt.show()

    def plot_complete_tag_diff(self):
        self.display_whole_img = True
        self.origx = (0, self.image.img.shape[1])
        self.origy = (self.image.img.shape[0],0)
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
            self.tags = pd.read_csv(self.path)
        except FileNotFoundError:
            self.error = (True, self.path)

    def load_processed_tags_from_tar(self, tar):
        try:
            self.tags = pd.read_csv(tar.extractfile(self.path))
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
        try:
            db = pd.read_csv(self.tag_db_path)
        except FileNotFoundError:
            db = pd.DataFrame()

        for a in add_attrs:
            tag['img_'+a] = getattr(self.image, a)
        # print(db.loc[:,("id","img_id", "img_time","img_date")])
        db = db.append(tag, ignore_index=True)
        db.img_time = db.img_time.astype(str).str.zfill(6)
        db.img_date = db.img_date.astype(str).str.zfill(8)
        db.img_id = db.img_id.astype(str).str.zfill(2)
        db.id = db.id.astype(int).astype(str)
        
        # remove duplicates
        db = self.remove_duplicates(db)
        db.sort_values(by=["img_date","img_id", "img_time","id"], ascending=True)
        # print(db.loc[:,("id","img_id", "img_time","img_date")])

        # save tagged image to folder according to a unique identifier
        self.copy_tag_image(tag)
        
        # save updated database
        db.to_csv(self.tag_db_path, index=False)

    def copy_tag_image(self, tag):
        from_path = os.path.join(
            os.path.dirname(self.image.path), 
            self.analysis, 
            "tag_image_orig",
            str(int(tag.id)) + ".tiff"
        )

        to_path = os.path.join(
            os.path.dirname(self.tag_db_path), 
            "annotated_images", 
             "_".join([
                 str(int(tag.img_date)).zfill(8), 
                 str(int(tag.img_id)).zfill(2), 
                 str(int(tag.img_time)).zfill(6), 
                 str(int(tag.id))
                 ])+".tiff"
        )

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
        duplicates = df.duplicated(subset=["id","img_id","img_date","img_time"], 
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

        self.save_new_tags(new_tags)

    def reset_lims(self):
        if self.display_whole_img:
            self.axes[0].set_xlim(self.origx)
            self.axes[0].set_ylim(self.origy)

    def show_original(self, resize=.1):
        img = cv.resize(self.image.img.copy(), (0,0), fx=resize, fy=resize)
        self.axes[0].imshow(self.image.img)

    def show_tagged(self):
        tagged = self.image.tag_image(self.image.img, self.new_tags['contour'])
        self.axes[0].imshow(tagged)

    def show_label(self):
        try:
            self.axes[1].annotate(self.ctag.label, (0.05,0.05), xycoords="axes fraction",
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
        for i in range(len(new_tags)):
            t = self.read_tag(new_tags, i)
            t.unpack_dictionaries()
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
        if self.display_whole_img:
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
    def combine_data_classic():
        data = Data.read_csv_list(glob("../data/pics_classic/results/*.csv"))
        meta = Data.read_csv_list(glob("../data/pics_classic/meta/*meta.csv"), 
                kwargs={"dtype":{"time":str,"id":int}})
        meta['picture'] = meta.groupby(["date","id"]).cumcount()
        df = data.merge(meta, how="left", on=["date","id", "picture"])

        # if there is an error it is because 
        m = pd.read_csv("../data/measurements.csv")
        m.rename(columns={"time":"date","ID_nano":"id"}, inplace=True)
        m['id'].fillna(0, inplace=True)
        m = m.astype({"id":int})
        df = df.merge(m, how="left", on=["date","id"])

        # manual observations --------------------------------------------------
        obs = Data.read_csv_list(glob("../data/raw_measurements/organisms/*.csv"), 
                kwargs={"dtype":{"time":str,"id":int}})
        obs.rename(columns={"time":"date","ID_nano":"id"}, inplace=True)
        df = df.merge(obs, "left", on=["date","id"])

        df["time"] = pd.to_datetime(df.date+df.time, format="%Y-%m-%d%H%M%S")
        df.set_index(["time","id", "picture"], inplace=True)
        df.drop(columns="date", inplace=True)
        df.to_csv("../data/pics_classic/data.csv", index=True)

        return df

    @staticmethod
    def read_csv_list(filenames, kwargs={}):
        df = pd.DataFrame()
        for filename in filenames:
            df = df.append(pd.read_csv(filename, **kwargs))

        return df
    
    @staticmethod
    def import_manual_measurements_one_file(path):
        """
        this method needs to be adapted to accomodate other sorts of 
        logged data.
        The most important point, is that the frame has a multiindex,
        consisting of 'time' and 'id'
        """
        df = pd.read_csv(path)  
        df = df.astype({'mntr_date': str, 'ID_nano': int, 
                        'conductivity': float, 'ID_measure': int})
        df['mntr_date'] = pd.to_datetime(df['mntr_date'])
        df.index = pd.MultiIndex.from_frame(df[['mntr_date', 'ID_measure']], names=['time','msr_id'])
        # mntr.index = pd.MultiIndex.from_frame(mntr[['mntr_date', 'ID_nano']], names=['time','id'])
        df = df.drop(columns=['mntr_date','ID_measure'])
        return df

    @staticmethod
    def import_photometer(path):
        """
        in preparation only the first row (column names) of the files need to be 
        modified: Change Verdünnung to Verduennung. Then no key errors will occurr.
        """
        files = Files.search_files(path, 'nutrients')
        corrections = Files.search_files(path, 'corrections')

        data = []
        for f in files:
            data.append(pd.read_csv(os.path.join(path,f), sep=","))

        df = pd.concat(data)
        df.dropna(how="all", inplace=True) # drop rows if all values are NA

        df['Timestamp'] = pd.to_datetime(df['SampleDate'], format="%d.%m.%Y")
        df = df.drop(columns=[
            "Verduennung","STAT","TYPE","Computer", "Anwender",  
            "send", "Dezimalen", "Bemerkung", "Einheit", "Datum", "Zeit", 
            "Probenort", "Methodennummer"
            ])

        df = df.rename(columns={"Timestamp":"time"})
        df = df.sort_values(["time","Zaehler"])
        df['msr_id'] = df.groupby(["time","Methodenname"]).cumcount()+1

        df = df.pivot(
            index=["time","msr_id"], 
            columns=["Methodenname"], 
            values=["Messwert","A","NTU","EST"]
            )
        
        # transofrm column multiindex to normal index
        df.columns = df.columns.to_series().apply('__'.join)

        df = df.rename(columns={
            "Messwert__AMMONIUM 15":"Ammonium",
            "Messwert__AMMONIUM 3" :"Ammonium_3",
            "Messwert__NITRAT" :"Nitrate",
            "Messwert__NITRIT" :"Nitrite",
            "Messwert__o-PHOSPHAT" :"Phosphate",
        })

        return df

    @staticmethod
    def import_manual_measurements(path):
        """
        transferrable method, which returns a dataframe of KNICK MUltioxy 907
        data. Data must be in CSV format with unicode encoding.

        param   indicates the measured paramter (O2, conductivity, ...)
                this string must be present in the filenames
        tag     is the TAG (Messstelle) set in the device
        """
        files = glob(path)

        pd.DataFrame
        data = []
        for f in files:
            data.append(pd.read_table(os.path.join(path,f), sep=","))

        df = pd.concat(data).sort_values('Timestamp')
        
        df['AnnotationText'] = df['AnnotationText'].fillna(999)
        df = df.astype({'AnnotationText': int})
        
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df = df.drop(columns=["SensoFace", "SensorOrderCode", "DeviceErrorFlag", 
                              "SensorSerialCode"])

        # some edits to columns
        df = df.rename(columns={'OxyConcentration':'oxygen', 
                                'CondConductance': 'conductivity',
                                'TemperatureCelsius':'temperature_device',
                                'OxyPartialPressure': 'partial_pressure'})

        try:
            df['oxygen'] = df['oxygen'] / 1000 # to mg/L
        except KeyError:
            pass
        # df['oxygen_unit'] = "mg_L"

        if tag is not None:
            df = df[df['LoggerTagName'] == tag]
            df = df.drop(columns=['LoggerTagName'])

        df.index = pd.MultiIndex.from_frame(df[['Timestamp', 'AnnotationText']], names=['time','msr_id'])
        df = df.drop(columns=["Timestamp", "AnnotationText"])

        return df


    @staticmethod
    def import_knick_logger(path, param=None, tag=None):
        """
        transferrable method, which returns a dataframe of KNICK MUltioxy 907
        data. Data must be in CSV format with unicode encoding.

        param   indicates the measured paramter (O2, conductivity, ...)
                this string must be present in the filenames
        tag     is the TAG (Messstelle) set in the device
        """
        if param is not None:
            files = Files.search_files(path, param)
        else:
            files = Files.find_files(path, 'csv')

        data = []
        for f in files:
            data.append(pd.read_table(os.path.join(path,f), sep=","))

        df = pd.concat(data).sort_values('Timestamp')
        
        df['AnnotationText'] = df['AnnotationText'].fillna(999)
        df = df.astype({'AnnotationText': int})
        
        df['Timestamp'] = pd.to_datetime(df['Timestamp'])
        df = df.drop(columns=["SensoFace", "SensorOrderCode", "DeviceErrorFlag", 
                              "SensorSerialCode"])

        # some edits to columns
        df = df.rename(columns={'OxyConcentration':'oxygen', 
                                'CondConductance': 'conductivity',
                                'TemperatureCelsius':'temperature_device',
                                'OxyPartialPressure': 'partial_pressure'})

        try:
            df['oxygen'] = df['oxygen'] / 1000 # to mg/L
        except KeyError:
            pass
        # df['oxygen_unit'] = "mg_L"

        if tag is not None:
            df = df[df['LoggerTagName'] == tag]
            df = df.drop(columns=['LoggerTagName'])

        df.index = pd.MultiIndex.from_frame(df[['Timestamp', 'AnnotationText']], names=['time','msr_id'])
        df = df.drop(columns=["Timestamp", "AnnotationText"])

        return df

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