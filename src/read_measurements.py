from image.analysis import Data
import pandas as pd

# create empty data frame with dates and measurement ids -----------------------
dti = pd.date_range("2020-10-23", pd.datetime.today(), freq="D")
mid = range(1,81)
index = pd.MultiIndex.from_product([dti, mid], names = ["time", "msr_id"])

m = pd.DataFrame(index = index)


# manual measurements ----------------------------------------------------------
path = "../data/raw_measurements/manual_measurements/raw_data.csv"
manual = Data.import_manual_measurements(path)

# knick ------------------------------------------------------------------------

# if tags need to be corrected this should be done in the data files. Why?
# Because if a 3rd person looks at this no one will understand. Also
# This would be way to tedius to implement here

path = '../data/raw_measurements/physicochemical_knick/'
grp = [pd.Grouper(freq='D', level='time'),"msr_id"]

o2 = Data.import_knick_logger(path, 'o2', "NANO2")
o2 = o2.groupby(grp).nth(1)

cond = Data.import_knick_logger(path, 'conductivity', "NANO2")
cond = cond.groupby(grp).last()

# merging happens here =) and it works like a charm ----------------------------
m = m.merge(manual, 'left', left_index=True, right_index=True)
m.update(o2  , join='left', overwrite=True, errors='raise')
m.update(cond, join='left', overwrite=True, errors='raise')
m.to_csv("../data/measurements.csv")



# TODO: temperature correction for conductivity and oxygen correction for 
#       measurement time. At the moment, unly the 2nd oxygen value is extracted
# TODO: Conductivity must be dated back