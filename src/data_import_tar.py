import os
import tarfile
import json
import pandas as pd
from matplotlib import pyplot as plt
from image.process import Image
from image.analysis import Data, Annotations
import evaluation.calc as calc

# f = tarfile.open("./data/annotations/moving_edge-20210321_2355-slim.tar")
# names = f.getnames()
# names.sort()
# i = Image()
# i.read_processed(json.load(f.extractfile(names[105])), import_image=False)
# i.tags = Annotations(image=i, analysis="moving_edge", tag_db_path="")
# i.tags.find_annotations(f)
# # i.tags.load_processed_tags_from_tar(f)

# import image data
d = Data("./data/annotations/work/schunckf/nanocosm/data/pics/", sample_id='56', date='all', img_num='all', 
         search_keyword="moving_edge", import_images=False,
         correct_path=(True, 0, './data/annotations/'))

d.collect()
d.index_images()
d.order()
