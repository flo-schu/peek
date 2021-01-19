from image.analysis import Data
import evaluation.calc as calc
from matplotlib import pyplot as plt

d = Data("../data/annotations/", sample_id='all', date='all', img_num='all', 
         search_keyword="motion_analysis", import_images=False,
         correct_path=(True, 3, '../data/annotations/'))

d.collect()
dat = calc.count_organisms(d.data)
dat = calc.id_average(dat)

ax = plt.subplot()
for i in dat.index.levels[1]:
    ax.plot(dat.xs(i, level = "id"))
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
