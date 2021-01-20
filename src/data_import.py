from image.analysis import Data
import evaluation.calc as calc
from matplotlib import pyplot as plt
import pandas as pd

d = Data("../data/annotations/", sample_id='all', date='20210105', img_num='all', 
         search_keyword="motion_analysis", import_images=False,
         correct_path=(True, 3, '../data/annotations/'))

d.collect()
d.index_images()
d.order()
d.import_logging_data()
dat = calc.count_organisms(d.data)
dat = calc.id_average(dat)

df = dat.merge(d.dlog, 'left', left_index=True, right_index=True)


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
