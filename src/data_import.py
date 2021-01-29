from image.analysis import Data
import evaluation.calc as calc
from matplotlib import pyplot as plt
import pandas as pd
import numpy as np
import itertools

# make empty frame
# create an empty measurement frame with dates from start ot end of the 
# experiment and msr_id from 1-80
# then use merge to add the manual measurements and msr_id <-> nano_id combis
# then use update to feed data from loggers
# (opt) then drop NA columns

dti = pd.date_range("2020-10-23", pd.datetime.today(), freq="D")
mid = range(1,81)
index = pd.MultiIndex.from_product([dti, mid], names = ["time", "msr_id"])

m = pd.DataFrame(index = index)


# manual measurements ----------------------------------------------------------
path = "../data/raw_measurements/manual_measurements/raw_data.csv"
manual = Data.import_manual_measurements(path)

# knick ------------------------------------------------------------------------

# if tags need to be corrected this should be done in the data files. Why?
# Because if a 3rd person looks at this no one will understand. Also
# This would be way to tedius to implement here

path = '../data/raw_measurements/physicochemical_knick/'
grp = [pd.Grouper(freq='D', level='time'),"msr_id"]

o2 = Data.import_knick_logger(path, 'o2', "NANO2")
o2 = o2.groupby(grp).nth(1)

cond = Data.import_knick_logger(path, 'conductivity', "NANO2")
cond = cond.groupby(grp).last()

# merging happens here =) and it works like a charm ----------------------------
m = m.merge(manual, 'left', left_index=True, right_index=True)
m.update(o2  , join='left', overwrite=True, errors='raise')
m.update(cond, join='left', overwrite=True, errors='raise')
m.to_csv("../data/measurements.csv")

m.index = pd.MultiIndex.from_frame(m[['time', 'ID_nano']])

# TODO: temperature correction for conductivity and oxygen correction for 
#       measurement time. At the moment, unly the 2nd oxygen value is extracted



d = Data("../data/annotations/", sample_id='all', date='20210105', img_num='all', 
         search_keyword="motion_analysis", import_images=False,
         correct_path=(True, 3, '../data/annotations/'))

d.collect()
d.index_images()
d.order()
dat = calc.count_organisms(d.data)
dat = calc.id_average(dat)

manm = Data.import_manual_measurements()
measurements = manm.merge(df, 'outer', left_index=True, right_index=True)
measurements.to_csv('../data/test.csv')

df = dat.merge(manm, 'left', left_index=True, right_index=True)


plt.plot(df['count'], df['pH'], 'o')
plt.plot(df['count'], df['oxygen'], 'o')
plt.plot(df['count'], df['conductivity'], 'o')



ax = plt.subplot()
for i in dat.index.levels[1]:
    ax.plot(dat.xs(i, level = "id"), color="grey")
ax.set_xlabel("time")
ax.set_ylabel("n organisms")
plt.show()


# filter by date
d.date="20201229"
d.collect()

# filter by id
d.id=42
d.collect()

# show data
d.data




# - [x] make sure image is not necessessary when Annotations class is initiated
# - [ ] write functions to plot the timeseries (Then I have at least the performance of 
#       Daphnia)
