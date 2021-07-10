import sys
from glob import glob
import pandas as pd
import numpy as np
from datetime import datetime as dt
sys.path.append("src")
from image.analysis import Data

# read all csv files and parse dates. Can deal with multiple date formats
obs = Data.read_csv_list(
    glob("data/raw_measurements/organisms/*.csv"), 
    kwargs={"dtype":{"time":str,"id":int}}
)
obs = obs.rename(columns={"ID_nano":"nano_id"}) \
         .dropna(how="all") 
# interpolate missing values -------------------------------------------
obs["time"] = pd.to_datetime(obs.time, format="%d.%m.%Y")

obs.to_csv("data/measurements/organisms.txt", index=False)