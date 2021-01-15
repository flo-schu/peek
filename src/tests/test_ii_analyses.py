import sys, os
myPath = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, myPath + '/../')

import pandas as pd
from image.process import Series
from image.analysis import Annotations, Data
from utils.manage import Files


def test_a_motion_analysis():
    path = "data/pics/test/00010101"
    nanos = [f for f in Files.find_subdirs(path) if f != "999"]
    for n in nanos:
        s = Series(os.path.join(path,n))

        diffs, contours, tagged_ims = s.motion_analysis(lag=1, smooth=12, thresh_binary=15, thresh_size=5)

        for i in s.images[1:]:
            a = Annotations(i, 'motion_analysis')
            a.read_new_tags(pd.DataFrame(i.new_tags))

        print("tagged nano {} from {}".format(n, len(nanos)))

def test_b_data_import():
    paths = Data.collect_paths("data/pics/test/", sample_id='all', date='all', img_num='all')
    images = Data.collect_files(paths, "motion_analysis", import_image=False)

    assert len(paths) == 3, paths
    assert len(images) == 3, images
    assert images[0].tags.error
    assert images[2].tags.error
    assert not images[1].tags.error
    assert len(images[1].tags.tags) > 0
