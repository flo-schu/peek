import numpy as np
import xarray as xr
from matplotlib import pyplot as plt
from datetime import timedelta
from matplotlib import ticker

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
# size_avg = pixels.groupby("measurement").map(mean).unstack()
# size_std = pixels.groupby("measurement").map(std).unstack()

tab_colors = ["black", "tab:green", "tab:blue", "tab:orange", "tab:red",
            "tab:violet", "tab:pink", "tab:brown"]

start = "2021-04-02"
end = "2021-08-19"
def plot_endpoint(arr: xr.DataArray, color="black", ax=None, label=None):
    if ax is None:
        fig, ax = plt.subplots(1,1)
    arr = arr.sel(time=slice(start, end))

    # plot organism count
    t = (arr.time - arr.time[0]) * 1e-9 / 86400
    # t = arr.time
    ax.plot(
        t, arr,
        color=color,
        alpha=.1 ,
        linestyle="",
        marker="o"
    )

    ymean = arr.mean("nano_id")
    ax.plot(
        t, ymean, color=color, alpha=.9, linewidth=2, label=label
    )

def plot_contaminations(ax):
    contaminations = np.array(
        ["2021-06-03", "2021-06-30", "2021-07-27", "2021-07-30"], 
        dtype="datetime64[ns]"
    )
    contaminations = contaminations - np.array(start, dtype="datetime64[ns]")
    contaminations = contaminations * 1e-9 / 86400
    ax.vlines(contaminations,  *ax.get_ylim(), 
        color="black", alpha=.75, linestyle="dotted")


# plot organism count
fig, axes = plt.subplots(5, 2, sharex=True, sharey="col")
for col, species in enumerate(data.species.values):
    for row, (conc, color) in enumerate(
        zip(data.attrs["esfenvalerate_treatments"], tab_colors)):
            nano_ids = data.where(data.treatment == conc, drop=True).nano_id
            arr = org_count.sel(species=species, nano_id=nano_ids)
            plot_endpoint(arr, color=color, ax=axes[row, col])

    axes[0, col].set_title(species)

# plot organism count overlain across all treatmentswith moving average
fig, axes = plt.subplots(1, 2, sharex=True, sharey="col")
for col, species in enumerate(data.species.values):
    for row, (conc, color) in enumerate(
        zip(data.attrs["esfenvalerate_treatments"], tab_colors)):
            nano_ids = data.where(data.treatment == conc, drop=True).nano_id
            arr = org_count.sel(species=species, nano_id=nano_ids)
            arr = arr.rolling(time=14).mean()
            plot_endpoint(arr, color=color, ax=axes[col])

    axes[col].set_title(species)


# plot manual neonate count
ds = data.count_D_neo
fig, axes = plt.subplots(1, 1, sharex=True, sharey="col")
axes.set_yscale("log")
axes.set_xlabel("time [days]")
axes.set_ylabel("neonate abundance")
axes.set_xlim(0,139)
axes.set_ylim(1,100)
for row, (conc, color) in enumerate(
    zip(data.attrs["esfenvalerate_treatments"], tab_colors)):

    nano_ids = data.where(data.treatment == conc, drop=True).nano_id
    arr = ds.sel(nano_id=nano_ids)
    arr = arr.dropna("time", "all") # drop all NA times
    arr = arr.rolling(time=7, center=True).mean()
    plot_endpoint(arr, color=color, ax=axes)
    axes.plot(np.nan, np.nan, label=conc, color=color)
plot_contaminations(axes)
fig.legend(loc="upper center", ncol=5, frameon=False, 
    title="Esfenvalerate concentration [ng/L]")
fig.savefig("results/figures/daphnia_neo_count.png")


# plot manual neonate count
ds = data.count_D_juvenile
fig, axes = plt.subplots(1, 1, sharex=True, sharey="col")
axes.set_yscale("log")
axes.set_xlabel("time [days]")
axes.set_ylabel("juvenile abundance")
axes.set_xlim(0,139)
axes.set_ylim(0.9,100)
for row, (conc, color) in enumerate(
    zip(data.attrs["esfenvalerate_treatments"], tab_colors)):

    nano_ids = data.where(data.treatment == conc, drop=True).nano_id
    arr = ds.sel(nano_id=nano_ids)
    arr = arr.dropna("time", "all") # drop all NA times
    arr = arr.rolling(time=7, center=True).mean()

    plot_endpoint(arr, color=color, ax=axes)
    axes.plot(np.nan, np.nan, label=conc, color=color)
plot_contaminations(axes)
fig.legend(loc="upper center", ncol=5, frameon=False, 
    title="Esfenvalerate concentration [ng/L]")
fig.savefig("results/figures/daphnia_juv_count.png")

# plot manual adult count
ds = data.count_D_adult
fig, axes = plt.subplots(1, 1, sharex=True, sharey="col")
axes.set_yscale("log")
axes.set_xlabel("time [days]")
axes.set_ylabel("adult abundance")
axes.set_xlim(0,139)
axes.set_ylim(0.9,30)
for row, (conc, color) in enumerate(
    zip(data.attrs["esfenvalerate_treatments"], tab_colors)):

    nano_ids = data.where(data.treatment == conc, drop=True).nano_id
    arr = ds.sel(nano_id=nano_ids)
    arr = arr.dropna("time", "all") # drop all NA times
    # arr = arr.rolling(time=7, center=True).mean()

    plot_endpoint(arr, color=color, ax=axes)
    axes.plot(np.nan, np.nan, label=conc, color=color)
plot_contaminations(axes)
fig.legend(loc="upper center", ncol=5, frameon=False, 
    title="Esfenvalerate concentration [ng/L]")
fig.savefig("results/figures/daphnia_adu_count_norunningavg.png")

# plot manual culex count
ds = data.culex_adults
fig, axes = plt.subplots(1, 1, sharex=True, sharey="col")
axes.set_yscale("log")
axes.set_xlabel("time [days]")
axes.set_ylabel("culex emerged abundance")
axes.set_xlim(0,139)
axes.set_ylim(0.9,30)
for row, (conc, color) in enumerate(
    zip(data.attrs["esfenvalerate_treatments"], tab_colors)):

    nano_ids = data.where(data.treatment == conc, drop=True).nano_id
    arr = ds.sel(nano_id=nano_ids)
    arr = arr.dropna("time", "all") # drop all NA times
    arr = arr.rolling(time=7, center=True).mean()

    plot_endpoint(arr, color=color, ax=axes)
    axes.plot(np.nan, np.nan, label=conc, color=color)
plot_contaminations(axes)
fig.legend(loc="upper center", ncol=5, frameon=False, 
    title="Esfenvalerate concentration [ng/L]")
fig.savefig("results/figures/culex_emerged_count.png")

# plot manual culex count
ds = data.culex_larvae
fig, axes = plt.subplots(1, 1, sharex=True, sharey="col")
axes.set_yscale("log")
axes.set_xlabel("time [days]")
axes.set_ylabel("culex larvae abundance")
axes.set_xlim(0,139)
axes.set_ylim(0.9,30)
for row, (conc, color) in enumerate(
    zip(data.attrs["esfenvalerate_treatments"], tab_colors)):

    nano_ids = data.where(data.treatment == conc, drop=True).nano_id
    arr = ds.sel(nano_id=nano_ids)
    arr = arr.dropna("time", "all") # drop all NA times
    arr = arr.rolling(time=7, center=True).mean()

    plot_endpoint(arr, color=color, ax=axes)
    axes.plot(np.nan, np.nan, label=conc, color=color)
plot_contaminations(axes)
fig.legend(loc="upper center", ncol=5, frameon=False, 
    title="Esfenvalerate concentration [ng/L]")
fig.savefig("results/figures/culex_larvae_count.png")


# TODO: check culex abundance measurements. They seem to be shifted by 3-4 days
#       this is probably the time from 1st weekly measurement to 2nd weekly meas
