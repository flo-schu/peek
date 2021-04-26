import sys
from glob import glob
import pandas as pd
import numpy as np
from datetime import datetime as dt
from datetime import timedelta
from matplotlib import pyplot as plt
from matplotlib import dates as mdates
from matplotlib import cm as cm
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
    
# format timestamp and correct time adjustment
df["time"] = pd.to_datetime(df["time"], format="%d.%m.%Y %H:%M")
tdelta = timedelta(hours=1)
clock_change = dt(year=2021, month=4, day=9, hour=12)
df["time"] = np.where(df["time"] > clock_change, df["time"] - tdelta, df["time"] + tdelta)

# convert back to string and split string into date and time
df["ts"] = df.time.apply(lambda x: x.strftime("%d.%m.%Y %H:%M"))
df["daytime"] = pd.to_datetime([t.split(" ")[1] for t in list(df["ts"])], format="%H:%M")
df["date"] = pd.to_datetime([t.split(" ")[0] for t in list(df["ts"])], format="%d.%m.%Y")

# replace values and prepare for matching
df["msr_id"] = df["msr_id"].fillna(999)
df["msr_id"] = np.where(df["msr_id"] == "PERMACOSM", "888", df["msr_id"])
df["msr_id"] = np.where(df["msr_id"] == "TEMPCOSM", "777", df["msr_id"])
df = df.astype({"msr_id": int})

df["oxygen"] = df["oxygen"] / 1000 # to mg/L


# analyse daily variation


dr = df.query("msr_id == 888").query("date > '2021-02-15'")  
dr = dr.query("date < '2021-03-10' | date > '2021-03-12'")  # 

g = pd.Grouper(freq="H")

t_mean = dr.set_index(["daytime"]).groupby(g).mean().reset_index()

fig = plt.figure(figsize=(10,5))
ax = fig.add_subplot(111)
ax.scatter(dr["daytime"], dr["temperature_device"], c=dr.date, alpha=.5)
ax.plot(t_mean["daytime"], t_mean["temperature_device"], c="black")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%H"))
ax.set_xlabel("time of day")
ax.set_ylabel("temperature")
# rotate and align the tick labels so they look better
fig.autofmt_xdate()

def expo_decay_positive(t, k, Tdiff, Tmin):
    return Tdiff * (1 - np.exp(-k * t)) + Tmin

x = t_mean.query("daytime >= '1900-01-01 05:00' & daytime < '1900-01-01 22:00'")["daytime"]
y = expo_decay_positive(np.arange(0,17,1), .18, 1.6, 19.4)
ax.plot(x, y, c="tab:orange", linestyle="--")

# now that I have an approximate model for the temperature increase
# parameterized with temperature diff (~1.6 °C)
# increase (decay) coefficient (0.18 °C/h) 
# I can invert the equation and get the start temperature (i.e.) temperature
# before lights turn on, which should be the coldest time. Once I have that
# I can easily calculate the temperature after 16 hours

# of course this assumes that the temperature model is parameterized 
# the same for each model. This is not a solid assumption, especially
# because I know that light intensities are unequal and there is cooling 
# going on. 

# The best option would probably be to spend one day to monitor temperature
# of the nanos and then parameterize a temperature model for each experimental 
# unit which shouldnt be too hard after today.

# then also the other values can be used to validate the model

df.to_csv("data/measurements/oxygen.txt", index=False)


df.query("date == '2021-04-09'")