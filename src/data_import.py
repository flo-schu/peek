from image.analysis import Data

d = Data("../data/annotations/", sample_id='all', date='all', img_num=2, search_keyword="motion_analysis", import_images=False)


d.collect()
d.data
d.date="20201229"
d.collect()
d.data


# - [x] make sure image is not necessessary when Annotations class is initiated