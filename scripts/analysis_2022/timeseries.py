import numpy as np
import xarray as xr
from matplotlib import pyplot as plt

data = xr.load_dataset("data/final_dataset.nc")

def nonnan(x):
    assert len(x.shape) == 1, "must be 1D"
    return x.dropna("organism_id")

def mean(x):
    return nonnan(x).mean()

def std(x):
    return nonnan(x).std()

pixels = data.pixels.stack(measurement=["time", "nano_id", "species"])

org_count = pixels.notnull().sum("organism_id").unstack()
size_avg = pixels.groupby("measurement").map(mean).unstack()
size_std = pixels.groupby("measurement").map(std).unstack()



def plot_endpoint(arr):
    arr = arr.sel(time=slice("2021-04-02", "2021-08-19"))
    fig, axes = plt.subplots(5, 2, sharex=True, sharey="col")
    tab_colors = ["black", "tab:green", "tab:blue", "tab:orange", "tab:red",
                "tab:violet", "tab:pink", "tab:brown"]

    for col, species in enumerate(data.species.values):
        for row, (conc, color) in enumerate(
            zip(data.attrs["esfenvalerate_treatments"], tab_colors)):
            nano_ids = data.where(data.treatment == conc, drop=True).nano_id

            # plot organism count
            axes[row, col].plot(
                (arr.time - arr.time[0]) * 1e-9 / 86400, 
                arr.sel(species=species, nano_id=nano_ids),
                color=color,
                alpha=.5 
                # marker="o"
            )

        axes[0,col].set_title(species)


plot_endpoint(org_count)