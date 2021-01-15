from image.analysis import Data

images = Data.collect("../data/pics/", search_keyword="motion_analysis", 
                      sample_id='all', date='all', img_num=2, import_image=False)
images[66].__dict__




# - [x] make sure image is not necessessary when Annotations class is initiated