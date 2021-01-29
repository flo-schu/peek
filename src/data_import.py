from image.analysis import Data
import evaluation.calc as calc
from matplotlib import pyplot as plt
import pandas as pd

# import measurements
m = pd.read_csv("../data/measurements.csv")
m['time'] = pd.to_datetime(m['time'])
m.index = pd.MultiIndex.from_frame(m[['time', 'ID_nano']], names=['time','id'])
m = m.drop(columns=["time","ID_nano"])

# import images
d = Data("../data/annotations/", sample_id='6', date='all', img_num='all', 
         search_keyword="motion_analysis", import_images=False,
         correct_path=(True, 3, '../data/annotations/'))

d.collect()
d.index_images()
d.order()

# process image data
dat = calc.count_organisms(d.data)
dat = calc.id_average(dat)

# merge image and measurement data
df = dat.merge(m, 'left', left_index=True, right_index=True)

# plot data
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
