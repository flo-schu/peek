import pandas as pd
import numpy as np
from numpy import nanmean, size


data = pd.read_csv("data/pics_classic/results/d_size.csv")

# exclude problem images
data = data.query(
        "~ (picture_number == 86 & date == '2021-05-20') |" +
        "~ (id == 55 & date == '2021-05-20') |" +
        "~ (id == 7 & date == '2021-06-22') |" +
        "~ (id == 24 & date == '2021-06-22') |" +
        "~ (id == 53 & date == '2021-07-02') |" +
        "~ (id == 29 & date == '2021-05-20')" 

    ) 

individuals = data.assign(pic_count = lambda x: x.groupby(["id", "date", "picture"]).value.transform(np.count_nonzero)) \
    .assign(max_count = lambda x: x.groupby(["id", "date"]).pic_count.transform(np.max)) \
    .assign(ismax = lambda x: x.pic_count == x.max_count) \
    .query("ismax") \
    .assign(pic_area = lambda x: x.groupby(["id", "date", "picture"]).value.transform(np.sum)) \
    .assign(max_area = lambda x: x.groupby(["id", "date"]).pic_area.transform(np.max)) \
    .assign(ismax = lambda x: x.pic_area == x.max_area) \
    .query("ismax") \
    .assign(first_pic = lambda x: x.groupby(["id", "date"]).picture.transform(np.min)) \
    .assign(isfirst = lambda x: x.picture == x.first_pic) \
    .query("isfirst") \
    .assign(length = lambda x: np.sqrt( x.value / 35.5)) \
    .assign(sizeclass = "None") \
    .assign(sizeclass = lambda x: np.where(x.length > 2.28, "D_adult", x.sizeclass)) \
    .assign(sizeclass = lambda x: np.where(x.length <= 2.28, "D_juvenile", x.sizeclass)) \
    .assign(sizeclass = lambda x: np.where(x.length <= 1.68, "D_neo", x.sizeclass)) \
    .query("sizeclass != 'None'") \
    .rename(columns={"pic_count":"count", "date":"time", "id":"nano_id"}) \
    .drop(columns=["picture_number", "analysis", "max_count", "ismax", "pic_area", "max_area", "first_pic", "isfirst"])


size_agg = individuals.groupby(["nano_id", "time", "picture","sizeclass"]) \
    .agg(func={"count": "count", "length": nanmean}) \
    .reset_index() \
    .pivot(index = ["nano_id", "time"], columns="sizeclass", values=["count", "length"]) 

size_agg.columns = ['_'.join(col).strip() for col in size_agg.columns.values]

size_agg.to_csv("data/measurements/daphnia.txt")

# counts = \
#     .groupby(["id", "date", "picture"]) \
#     .agg(func={"analysis":"size", "value":"mean"}) \
#     .rename(columns={"analysis":"daphnia_count", "value":"daphnia_size", "date":"time", "id":"nano_id"}) \
#     .groupby(["nano_id", "time"]) \
#     .agg(func={"daphnia_count":"max","daphnia_size":"mean"}) 

# data.to_csv("data/measurements/daphnia.txt")
