from image.analysis import Data
import evaluation.calc as calc
from matplotlib import pyplot as plt
import pandas as pd

# import measurements
# m = pd.read_csv("../data/measurements.csv")
# m['time'] = pd.to_datetime(m['time'])
# m.index = pd.MultiIndex.from_frame(m[['time', 'ID_nano']], names=['time','id'])
# m = m.drop(columns=["time","ID_nano"])

# import image data
d = Data("../data/annotations/", sample_id='6', date='all', img_num='all', 
         search_keyword="motion_analysis", import_images=False,
         correct_path=(True, 3, '../data/annotations/'))

d.collect()
d.index_images()
d.order()
