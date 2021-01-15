from image.analysis import Data

paths = Data.collect_paths("../data/pics/test", sample_id='all', date='all', img_num=2)
images = Data.collect_files(paths, "motion_analysis", import_image=False)
images[66].__dict__




# - [x] make sure image is not necessessary when Annotations class is initiated