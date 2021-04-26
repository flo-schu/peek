import sys
from glob import glob
import pandas as pd
import numpy as np
sys.path.append("src")
from image.analysis import Data

# read data
df = Data.read_csv_list(glob("data/raw_measurements/physicochemical_knick/*o2.csv"))

# discard unneeded columns and rename
df = df.drop(columns=["SensoFace", "SensorOrderCode", "DeviceErrorFlag", 
                        "SensorSerialCode", "AnnotationText"])

df = df.rename(columns={"OxyConcentration":"oxygen", 
                        "TemperatureCelsius":"temperature_device",
                        "OxyPartialPressure": "partial_pressure",
                        "LoggerTagName":"msr_id",
                        "Timestamp":"time"})
    
# format timestamp
df["time"] = pd.to_date_time(df["time"], format="%d.%m.%Y %H:%M")

# replace values and prepare for matching
df["msr_id"] = df["msr_id"].fillna(999)
df["msr_id"] = np.where(df["msr_id"] == "PERMACOSM", "888", df["msr_id"])
df["msr_id"] = np.where(df["msr_id"] == "TEMPCOSM", "777", df["msr_id"])
df = df.astype({"msr_id": int})

df["oxygen"] = df["oxygen"] / 1000 # to mg/L

df.to_csv("data/measurements/oxygen.txt", index=False)
