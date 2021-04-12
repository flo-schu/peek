from image.analysis import Data
import pandas as pd
import numpy as np
from datetime import datetime as dt
from glob import glob

# before importing take steps named in raw_measurements/readme.txt

# create empty data frame with dates and measurement ids -----------------------
dti = pd.date_range("2020-10-23", dt.today(), freq="D")
mid = range(1,81)
index = pd.MultiIndex.from_product([dti, mid], names = ["time", "msr_id"])

m = pd.DataFrame(index = index)
m["EST__NITRAT"] = np.nan
m["EST__AMMONIUM 3"] = np.nan
m["EST__AMMONIUM 15"] = np.nan
m["EST__NITRIT"] = np.nan
m["EST__o-PHOSPHAT"] = np.nan


# photometer measurements (nutrients) ------------------------------------------
path = "data/raw_measurements/nutrients_photometer_mn/"
photom = Data.import_photometer(path)
test = photom.reset_index()

# at the moment only the actual measured values are imported. If other columns
# should be imported they can be specified in the m.assign() block in line 15

# manual measurements ----------------------------------------------------------
manual = Data.read_csv_list(glob("data/raw_measurements/manual_measurements/dates/*.csv"))
manual["time"] = pd.to_datetime(manual.mntr_date, format="%Y%m%d")
manual.rename(columns={"ID_measure":"msr_id"}, inplace=True)
manual.set_index(["time","msr_id"], inplace=True)
manual.drop(columns="mntr_date", inplace=True)
# knick ------------------------------------------------------------------------

# if tags need to be corrected this should be done in the data files. Why?
# Because if a 3rd person looks at this no one will understand. Also
# This would be way to tedius to implement here

path = 'data/raw_measurements/physicochemical_knick/'
grp = [pd.Grouper(freq='D', level='time'),"msr_id"]

o2 = Data.import_knick_logger(path, 'o2', "NANO2")
o2 = o2.groupby(grp).nth(1)

cond = Data.import_knick_logger(path, 'conductivity', "NANO2")
cond = cond.groupby(grp).last()

# merging happens here =) and it works like a charm ----------------------------
m = m.merge(manual, 'left', left_index=True, right_index=True)
m.update(o2    , join='left', overwrite=True, errors='raise')
m.update(cond  , join='left', overwrite=True, errors='raise')
m.update(photom, join='left', overwrite=True, errors='raise')
m = m.dropna(how="all")
m.to_csv("data/measurements.csv")



# TODO: temperature correction for conductivity and oxygen correction for 
#       measurement time. At the moment, unly the 2nd oxygen value is extracted
# TODO: Conductivity must be dated back