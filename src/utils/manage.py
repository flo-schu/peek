import os
import shutil
import imageio
import pandas as pd
import numpy as np
from dateutil.parser import parse

class Files:
    @staticmethod
    def append_to_filename(path, app):
        return os.path.join(os.path.dirname(path),os.path.basename(path).split(".")[0]+app)

    def change_file_ext(self, new_ext=""):
        fname, old_ext = os.path.splitext(self.path)
        if new_ext == "":
            new_ext = old_ext

        self.path = fname+new_ext
        return self.path

    def change_dir(self, subdir):
        return os.path.join(os.path.dirname(self.path), subdir,"")

    def create_dir(self, subdir):
        path = self.change_dir(subdir)
        if not os.path.exists(path):
            os.mkdir(path)
        return path

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
    def browse_subdirs_for_files(cls, path, file_type):
        dirs = cls.find_subdirs(path)
        struct = {}
        for i, d in enumerate(dirs):
            p = cls.find_single_file(os.path.join(path, d), file_type)
            struct.update({str(i):p})
        return struct

    @classmethod
    def find_single_file(cls, directory, file_type):
        f = cls.find_files(path=directory, file_type=file_type)
        assert len(f) == 1, print(f)
        return os.path.join(directory, f[0])

    @classmethod
    def find_files(cls, path, file_type=""):
        # remove subdirectories
        basedir = os.path.join(path, "")
        files = cls.search_files(basedir)
        if file_type != "":
            # remove files that are not of type e.g. "RW2" or "tiff", etc.
            files = [i  for i in files if i.split(".")[1] == file_type]   
        
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

    def save(self, attr="img", file_ext="", remove_from_instance=False):
        if remove_from_instance:
            obj = self.__dict__.pop(attr)
        else:
            obj = getattr(self, attr)

        imageio.imwrite(self.change_file_ext(file_ext), obj)

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
