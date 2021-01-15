from image.analysis import Data

d = Data("../data/annotations/", sample_id='all', date='all', img_num=2, search_keyword="motion_analysis", import_images=False)


d.collect()

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
