import pandas as pd
import sys
sys.path.append("src")
import evaluation.calc as calc
from numpy import nanmean

data = pd.read_csv("data/pics_classic/results/c_immo_size.csv") \
    .append(pd.read_csv("data/pics_classic/results/c_mobile_size.csv"))


data = data.groupby(["id", "date", "picture"]) \
    .agg(func={"analysis":"size", "value":"mean"}) \
    .reset_index() \
    .rename(columns={"analysis":"culex_count", "value":"culex_size", "date":"time", "id":"nano_id"}) \
    .groupby(["nano_id", "time"]) \
    .agg(func={"culex_count":"max","culex_size":nanmean})

data.to_csv("data/measurements/culex.txt")

