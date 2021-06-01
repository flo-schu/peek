import pandas as pd
import sys
sys.path.append("src")
import evaluation.calc as calc

data = pd.read_csv("data/pics_classic/results/d_size.csv") \
    .query(
        "~ (picture_number == 86 & date == '2021-05-20') |" +
        "~ (id == 55 & date == '2021-05-20')"
    ) \
    .groupby(["id", "date", "picture"]) \
    .agg(func={"analysis":"size", "value":"mean"}) \
    .reset_index() \
    .rename(columns={"analysis":"daphnia_count", "value":"daphnia_size", "date":"time", "id":"nano_id"}) \
    .groupby(["nano_id", "time"]) \
    .agg(func={"daphnia_count":"max","daphnia_size":"mean"}) 

data.to_csv("data/measurements/daphnia.txt")

