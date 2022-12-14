import os
import json
import shutil
import imageio
import pandas as pd
import numpy as np
from dateutil.parser import parse

class Files:
    @staticmethod
    def append_to_filename(path, app):
        return os.path.join(os.path.dirname(path),os.path.basename(path).split(".")[0]+app)

    def change_file_ext(self, new_ext="", inplace=True):
        fname, old_ext = os.path.splitext(self.path)
        if new_ext == "":
            new_ext = old_ext

        path = fname+new_ext

        if inplace:
            self.path = path

        return path

    def change_dir(self, subdir):
        return os.path.join(os.path.dirname(self.path), subdir,"")

    def create_dir(self, subdir):
        path = self.change_dir(subdir)
        # if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)
        return path

    @staticmethod
    def file_exist(path):
        return os.path.exists(path)

    @classmethod
    def check_if_exist(cls, path, dirlist):
        return [os.path.exists(os.path.join(path, d)) for d in dirlist]

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

    @staticmethod
    def find_subdirs(path):
        # remove subdirectories
        return [f.name for f in os.scandir(path) if not f.is_file()]

    @staticmethod
    def search_files(path, search_string=None):
        files = [f.name for f in os.scandir(path) if f.is_file()]

        if search_string is None:
            return files
        else:
            return [f for f in files if search_string in f]

    @classmethod
    def browse_subdirs_for_files(cls, path, file_type, return_full_path=False):
        dirs = cls.find_subdirs(path)
        struct = {}
        i = 0
        for d in dirs:
            subpath = os.path.join(path, d)
            files = cls.find_files(subpath, file_type)
            for f in files: 
                struct.update({str(i):os.path.abspath(os.path.join(subpath, f))})
                i += 1
        # print(struct)
        
        return struct

    @classmethod
    def find_single_file(cls, directory, file_type):
        f = cls.find_files(path=directory, file_type=file_type)
        assert len(f) == 1, print('more than 1 file', f)
        return os.path.join(directory, f[0])

    @classmethod
    def find_files(cls, path, file_type=""):
        # remove subdirectories
        basedir = os.path.join(path, "")
        files = cls.search_files(basedir)
        if file_type != "":
            # remove files that are not of type e.g. "RW2" or "tiff", etc.
            files = [f for f in files if file_type in f]   
        
        return files

    def read_image(self, attr="img", file_ext=""):
        value = imageio.imread(self.change_file_ext(file_ext))
        setattr(self, attr, value)

    @staticmethod
    def read(path):
        dirname = os.path.dirname(path)
        basename = os.path.basename(path)
        f_name = basename.split(".")[0]
        f_ext = basename.split(".")[1]
        if f_ext == "npy":
            return np.load(path)

        if f_ext == "tiff":
            return imageio.imread(path)

        if f_ext == "csv":
            return pd.read_csv(path)

        else:
            print("error. Most likely unknown filetype for read function")

    def save(self, attr="img", file_ext="", remove_from_instance=False, modify_path=True):
        if remove_from_instance:
            obj = self.__dict__.pop(attr)
        else:
            obj = getattr(self, attr)

        imageio.imwrite(self.change_file_ext(file_ext, inplace=modify_path), obj)

    @staticmethod
    def is_date(string, fuzzy=False):
        """
        Return whether the string can be interpreted as a date.

        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        try: 
            parse(string, fuzzy=fuzzy)
            return True

        except ValueError:
            return False

    @staticmethod
    def filter_files(path, ex1, ex2):
        """
        much better filter function. Two conditions
        """
        flist = []
        for p, dirs, fls in os.walk(path):
            fls[:] = [f for f in fls if not (ex1 in f and ex2 in f)]   
            flist.extend([os.path.join(p, f) for f in fls])
        return flist

    @classmethod    
    def copy_files(cls, path, new_path, ex1='.tiff', ex2="PNAN"):
        old_files = cls.filter_files(path, ex1, ex2)
        new_files = [f.replace(path, new_path) for f in old_files]

        for of, nf in zip(old_files, new_files):
            os.makedirs(os.path.dirname(nf), exist_ok=True)
            shutil.copyfile(of, nf)

    @staticmethod
    def change_top_dirs(path, strip_levels=0, add_path=""):
        path = os.path.normpath(path)
        pparts = [add_path] + path.split(os.sep)[strip_levels:]
        return os.path.join(*pparts)

    @staticmethod
    def change_root_of_path(path, new_root="", trim_path_until=""):
        path = os.path.normpath(path)
        new_root = os.path.normpath(new_root)

        pattern = os.path.normpath(trim_path_until)+os.sep
        top_dir = path[path.index(pattern)+len(pattern):]

        return os.path.join(new_root, top_dir)

    @staticmethod
    def read_settings(path=""):
        if os.path.basename(path) == "":
            return {}
            
        with open(path, "r") as f:
            pars = json.load(f)

        return pars

    @staticmethod    
    def get_folders_excluding(path, exclude=[]):
        folders = set(Files.find_subdirs(path))
        for ex in exclude:
            folders = folders.difference([ex])

        return list(sorted(folders))

    @staticmethod
    def load_settings_dir():
        return os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), 
                '..', '..', 
                'settings'
                )
            )
