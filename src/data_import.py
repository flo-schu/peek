from image.analysis import Data


d = Data("../data/annotations/", sample_id='42', date='all', img_num='all', 
         search_keyword="motion_analysis", import_images=False,
         correct_path=(True, 3, '../data/annotations/'))
d.collect()
d.data
len(d.data)

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
df = d.data


dat = df.groupby(['time','id']).size()
agg = dat.groupby([pd.Grouper(freq='D', level='time'), 'id']).mean()


ax = plt.subplot(111)
i=1

ax = ax.plot(agg.xs(3, level = "id"), 'o')
for i in agg.index.levels[1]:
    ax.plot(agg.xs(i, level = "id"), 'o')


fig = plt.figure()
ax1 = fig.add_subplot(211)
ax1.plot([1,2,3],[1,2,3])
plt.show()

plt.plot(agg.xs(i, level = "id"))




from evaluation.calc import count_organisms
dat = count_organisms(d.data)






d.data.loc["2020-12-17"]

d.data.xs(2, level = "id")

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
