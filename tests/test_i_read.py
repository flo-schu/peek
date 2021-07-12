import sys
sys.path.append("src")

from utils.manage import Files
from image.process import Session
from image.analysis import Data
from distutils.dir_util import copy_tree
import pytest


# backup = "data/pics/test/test_images"
# work = "data/pics/test/00010101"

# def test_a_read_session():
#     copy_tree(backup, work)
#     s = Session(work)
#     s.read_images(stop_after=None)

# def test_b_read_output():
#     paths = Data.collect_paths("data/pics/test", sample_id='all', date='all', img_num='all')
#     assert len(paths) == 3, paths
#     assert all([os.path.exists(p) for p in paths]), os.listdir(work)
