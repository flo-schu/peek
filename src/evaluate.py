from image.analysis import Data
from evaluation.main import analyse, save

# import image data
d = Data("./data/annotations/work/schunckf/nanocosm/data/pics/",
         search_keyword="moving_edge", import_images=False,
         correct_path=(True, 0, './data/annotations/'))

# analyse(data=d, algorithm="count_and_average_over_id", plot="show_ts", sample_id="10")
# analyse(data=d, algorithm="count_and_average_over_id", plot="show_ts", sample_id="17")

save(d, "./data/results/ts.csv", date="20210302")

