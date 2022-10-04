import sys
from glob import glob
import pandas as pd

sys.path.append("src")
from image.analysis import Data

manual = Data.read_csv_list(glob("data/raw_measurements/manual_measurements/dates/*.csv"))
manual["time"] = pd.to_datetime(manual.mntr_date, format="%Y%m%d")
manual.rename(columns={"ID_measure":"msr_id", "ID_nano":"nano_id"}, inplace=True)
manual.drop(columns="mntr_date", inplace=True)

manual[["time","msr_id","nano_id"]].to_csv("data/measurements/match.txt",index=False)

manual[["time","msr_id","temperature"]].to_csv("data/measurements/temperature.txt", index=False)