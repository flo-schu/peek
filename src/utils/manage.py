import os
import shutil
import imageio

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

    def browse_subdirs_for_files(self, file_type):
        dirs = self.find_subdirs(self.path)
        struct = {}
        for i, d in enumerate(dirs):
            f = self.find_files(subdir=d, file_type=file_type)
            assert len(f) == 1, print(f)
            path = os.path.join(self.path, d, f[0])
            struct.update({str(i):path})
        return struct

    def find_files(self, subdir="", file_type=""):
        # remove subdirectories
        basedir = os.path.join(self.path, subdir)
        files = [f.name for f in os.scandir(basedir) if f.is_file()]
        if file_type != "":
            # remove files that are not of type e.g. "RW2" or "tiff", etc.
            files = [i  for i in files if i.split(".")[1] == file_type]   
        
        return files

    def read(self, attr="img", file_ext=""):
        value = imageio.imread(self.change_file_ext(file_ext))
        setattr(self, attr, value)

    def save(self, attr="img", file_ext="", remove_from_instance=False):
        if remove_from_instance:
            obj = self.__dict__.pop(attr)
        else:
            obj = getattr(self, attr)

        imageio.imwrite(self.change_file_ext(file_ext), obj)
