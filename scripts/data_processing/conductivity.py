import sys
from glob import glob
import pandas as pd
import numpy as np
sys.path.append("src")
from image.analysis import Data



manual = Data.read_csv_list(glob("data/raw_measurements/manual_measurements/dates/*.csv"))
manual["time"] = pd.to_datetime(manual.mntr_date, format="%Y%m%d")
manual.rename(columns={"ID_measure":"msr_id", "ID_nano":"nano_id"}, inplace=True)
manual.drop(columns="mntr_date", inplace=True)

cond_man = manual[["time","msr_id","conductivity"]].set_index(["time","msr_id"])
cond_man = cond_man.dropna(how="all")
# read data
df = Data.read_csv_list(
    glob("data/raw_measurements/physicochemical_knick/*conductivity.csv"))

# discard unneeded columns and rename
df = df.drop(columns=["SensoFace", "SensorOrderCode", "DeviceErrorFlag", 
                        "SensorSerialCode", "AnnotationText"])

df = df.rename(columns={"CondConductance": "conductivity",
                        "TemperatureCelsius":"temperature_device",
                        "LoggerTagName":"msr_id",
                        "Timestamp":"time"})
    
# format timestamp
df["time"] = pd.to_datetime(df["time"], format="%d.%m.%Y %H:%M")

# replace values and prepare for matching
df["msr_id"] = df["msr_id"].fillna(999)
df["msr_id"] = np.where(df["msr_id"] == "PERMACOSM", "888", df["msr_id"])
df["msr_id"] = np.where(df["msr_id"] == "TEMPCOSM", "777", df["msr_id"])
df = df.astype({"msr_id": int})




# save
df0 = cond_man
df1 = df[["time","msr_id","conductivity"]].set_index(["time","msr_id"])
# save nth value (no computation involved)
grp = [pd.Grouper(freq="D", level="time"),"msr_id"]
df1 = df1.groupby(grp).last()

conductivity = pd.concat([df0, df1])


conductivity.to_csv("data/measurements/conductivity.txt")
