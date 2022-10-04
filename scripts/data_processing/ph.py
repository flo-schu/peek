import sys
from glob import glob
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import dates as mdates


sys.path.append("src")
from image.analysis import Data

manual = Data.read_csv_list(glob("data/raw_measurements/manual_measurements/dates/*.csv"))
manual["time"] = pd.to_datetime(manual.mntr_date, format="%Y%m%d")
manual.rename(columns={"ID_measure":"msr_id", "ID_nano":"nano_id"}, inplace=True)
manual.drop(columns="mntr_date", inplace=True)

ph_man = manual[["time","msr_id","pH"]] \
    .set_index(["time","msr_id"]) \
    .dropna(how="all")

# read data
df = Data.read_csv_list(
    glob("data/raw_measurements/physicochemical_knick/*ph.csv"))

# discard unneeded columns and rename

df = df.rename(columns={"PhPh": "pH",
                        "TemperatureCelsius":"temperature_device",
                        "LoggerTagName":"msr_id",
                        "Timestamp":"time"})
                        
df = df.drop(columns=["SensoFace", "SensorOrderCode", "DeviceErrorFlag", 
                        "SensorSerialCode", "AnnotationText", "PhVoltage"])
    
# format timestamp

df["time"] = pd.to_datetime(df["time"], format="%d.%m.%Y %H:%M:%S")

# replace values and prepare for matching
df["msr_id"] = df["msr_id"].fillna(999)
df["msr_id"] = np.where(df["msr_id"] == "PERMACOSM", "888", df["msr_id"])
df = df.astype({"msr_id": int})

df["ts"] = df.time.apply(lambda x: x.strftime("%d.%m.%Y %H:%M:%S"))
df["daytime"] = pd.to_datetime([t.split(" ")[1] for t in list(df["ts"])], format="%H:%M:%S")
df["date"] = pd.to_datetime(df.SampleDate, format="%d.%m.%Y")

# ph daily variation

dr = df.query("msr_id == 888").reset_index()

g = pd.Grouper(freq="H")

t_mean = dr.set_index(["daytime"]).groupby(g).mean().reset_index()

fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(111)
ax.scatter(dr["daytime"], dr["pH"], alpha=.5)
ax.plot(t_mean["daytime"], t_mean["pH"], c="black")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H"))
ax.set_xlabel("time of day")
ax.set_ylabel("pH")
# rotate and align the tick labels so they look better
fig.autofmt_xdate()
plt.savefig("plots/ph_daily_variation.png")

# pH convergence

d = df.query("msr_id == 48 & date == '20210507'")
plt.plot(d.time, d.pH, "o", alpha=.5)



# save pH measurements
df = df.drop(columns=["time", "daytime", "ts", "temperature_device", "SampleDate"])
df = df.rename(columns={"date":"time"})
df = df.set_index(["time","msr_id"])


# save nth value (no computation involved)
nanos = df.query("msr_id <= 100")
grp = [pd.Grouper(freq="D", level="time"),"msr_id"]
df1 = nanos.groupby(grp).last()

# ph = pd.concat([ph_man,df1])
ph = df1
ph.to_csv("data/measurements/ph.txt")

