import pandas as pd
import sys
from numpy import nanmean
import xarray as xr
import numpy as np

data = pd.read_csv("data/pics_classic/results/c_immo_size.csv") \
    .append(pd.read_csv("data/pics_classic/results/c_mobile_size.csv"))


data = data.query(
        "~ (picture_number == 39 & date == '2021-04-27') |" +
        "~ (picture_number == 48 & date == '2021-05-24') " 
    ) \
    .rename(columns={"value":"pixels", "date":"time", "id":"nano_id"})

xrdata = data.drop(columns=["picture", "picture_number", "analysis"])
xrdata["organism_id"] = xrdata.groupby(["time", "nano_id", "species"]).cumcount()

n_max = xrdata.organism_id.max() + 1
nans = np.repeat(np.nan, n_max)
master_array = xr.DataArray()
for (t, nid, spec), group in xrdata.groupby(["time", "nano_id", "species"]):
    values = nans.copy()
    pixels = np.nan_to_num(group.pixels.values, nan=0).astype(int)
    pixels = pixels[pixels != 0]
    values[0:len(pixels)] = pixels
    values = values.reshape((1, 1, 1, n_max))
    coords = {
        "time": np.array([t]), 
        "nano_id": np.array([nid]), 
        "species": np.array([spec]), 
        "organism_id": range(values.shape[-1])
    }
    da = xr.DataArray(values, coords=coords, name="pixels")
    master_array = master_array.combine_first(da)

master_array.to_netcdf("data/measurements/culex_raw.nc")