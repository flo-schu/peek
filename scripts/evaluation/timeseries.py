import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

def stacked_plot(df, ax, **kwargs):
    df.insert(0, "zero", 0)
    cdat = df.cumsum(axis=1)

    for col in np.arange(1, cdat.shape[1]):
        ax.fill_between(
            cdat.index, 
            cdat.iloc[:, col-1], 
            cdat.iloc[:, col],
            label = cdat.columns[col],
            **kwargs
        )

data = pd.read_csv("data/measurements.csv", index_col="time", infer_datetime_format=True, parse_dates=["time"])
nano = data.query("id==80").query("time > '2021-04-06'")

# open figure
fig = plt.figure()

# Ax 1: Culex timeseries
nano["culex_small"] = nano["culex_small"]
sdata = nano.dropna(how="all") \
    .loc[:, ["culex_small", "culex_larvae", "culex_pupae", "culex_adults"]] \
    .interpolate("time",limit_direction="forward") \
    .fillna(0) \
    .rolling("14d").mean() 

ax1 = fig.add_subplot(311, label="Cl")
ax1.text(0.01,0.85,"Culex", transform=ax1.transAxes)
stacked_plot(sdata, ax1, alpha=.6)
ax1.set_xticks([])
ax1.scatter(nano.index, np.where(nano.culex_repro > 0, 1, np.nan))
ax1.set_ylabel("abundance")
ax1.legend(ncol=2, labels=["hatched", "larvae", "pupae", "adults"])

# Ax 2: Daphnia timeseries
sdata = nano.dropna(how="all") \
    .loc[:, "daphnia_count"] \
    .interpolate("time",limit_direction="forward") \
    .rolling("7d").mean() \
    .to_frame()

ax2 = fig.add_subplot(312, sharex=ax1, label="Dc")
ax2.set_ylabel("abundance")
ax2.text(0.01,0.85,"Daphnia", transform=ax2.transAxes)
stacked_plot(sdata, ax2, alpha=.6)
# ax2.set_ylim(0,50)

size = nano["daphnia_size"] \
    .interpolate("time",limit_direction="forward") \
    .rolling("7d").mean() \
    .to_frame()

ax2r = fig.add_subplot(312, sharex=ax2, frameon=False, label="Ds")
l = ax2r.plot(size.index, size.daphnia_size, "--", label="size")
ax2r.yaxis.tick_right()
ax2r.set_ylabel("size")
ax2r.yaxis.set_label_position("right")
# ax2r.set_ylim(0,100)

algae = nano["algae_volume"] \
    .interpolate("time",limit_direction="forward") \
    .rolling("7d").mean()

ax3 = fig.add_subplot(313, sharex=ax1, label="oxy")
ax3.plot(algae, label="algae density")
ax3.legend()
# ax4 = fig.add_subplot(514, sharex=ax1, label="po4")
# ax4.plot(nano.index, nano["NH4"])

fig.autofmt_xdate()

