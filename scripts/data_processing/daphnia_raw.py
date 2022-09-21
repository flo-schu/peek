import pandas as pd
import numpy as np
from numpy import nanmean, size
import xarray as xr


data = pd.read_csv("data/pics_classic/results/d_size.csv")

# exclude problem images
data = data.query(
        "~ ( (picture_number == 86 & date == '2021-05-20') |" +
        "    (id == 55 & date == '2021-05-20') |" +
        "    (id == 7 & date == '2021-06-22') |" +
        "    (id == 24 & date == '2021-06-22') |" +
        "    (id == 53 & date == '2021-07-02') |" +
        "    (id == 29 & date == '2021-05-20') )" 

    ) 

individuals = data.assign(pic_count = lambda x: x.groupby(["id", "date", "picture"]).value.transform(np.count_nonzero)) \
    .assign(max_count = lambda x: x.groupby(["id", "date"]).pic_count.transform(np.max)) \
    .assign(ismax = lambda x: x.pic_count == x.max_count) \
    .query("ismax") \
    .assign(pic_area = lambda x: x.groupby(["id", "date", "picture"]).value.transform(np.sum)) \
    .assign(max_area = lambda x: x.groupby(["id", "date"]).pic_area.transform(np.max)) \
    .assign(ismax = lambda x: x.pic_area == x.max_area) \
    .query("ismax") \
    .assign(first_pic = lambda x: x.groupby(["id", "date"]).picture.transform(np.min)) \
    .assign(isfirst = lambda x: x.picture == x.first_pic) \
    .query("isfirst") \
    .assign(length = lambda x: np.sqrt( x.value / 25.5)) \
    .assign(sizeclass = "None") \
    .assign(sizeclass = lambda x: np.where(x.length > 2.28, "D_adult", x.sizeclass)) \
    .assign(sizeclass = lambda x: np.where(x.length <= 2.28, "D_juvenile", x.sizeclass)) \
    .assign(sizeclass = lambda x: np.where(x.length <= 1.68, "D_neo", x.sizeclass)) \
    .query("sizeclass != 'None'") \
    .rename(columns={"pic_count":"count", "date":"time", "id":"nano_id"}) \
    .drop(columns=["picture_number", "analysis", "max_count", "ismax", "pic_area", "max_area", "first_pic", "isfirst"])


xrdata = individuals.drop(columns=["picture", "count", "length", "sizeclass"])
xrdata["organism_id"] = xrdata.groupby(["time", "nano_id", "species"]).cumcount()
xrdata = xrdata.rename(columns={"value":"pixels"})

n_max = xrdata.organism_id.max() + 1
zeros = np.zeros(n_max, dtype=int)
master_array = xr.DataArray()
for (t, nid, spec), group in xrdata.groupby(["time", "nano_id", "species"]):
    values = zeros.copy()
    pixels = np.nan_to_num(group.pixels.values, nan=0).astype(int)
    pixels = pixels[pixels != 0]  # delete any detected nan origanisms
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

master_array.to_netcdf("data/measurements/daphnia_raw.nc")