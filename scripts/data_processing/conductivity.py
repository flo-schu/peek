import sys
from glob import glob
import pandas as pd
import numpy as np
sys.path.append("src")
from image.analysis import Data

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


df.to_csv("data/measurements/conductivity.txt", index=False)
