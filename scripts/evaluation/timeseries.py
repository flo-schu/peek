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
nano = data.query("id==2").query("time > '2021-04-06'")
contaminations = []

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
ax1.vlines()
ax1.set_ylabel("abundance")
ax1.legend(ncol=2, labels=["hatched", "larvae", "pupae", "adults"])

# Ax 2: Daphnia timeseries
sdata = nano.dropna(how="all") \
    .loc[:, ["count_D_adult", "count_D_juvenile", "count_D_neo"]] \
    .interpolate("time",limit_direction="forward") \
    .rolling("7d").mean() 

ax2 = fig.add_subplot(312, sharex=ax1, label="Dc")
ax2.set_ylabel("abundance")
ax2.text(0.01,0.85,"Daphnia", transform=ax2.transAxes)
stacked_plot(sdata, ax2, alpha=.6)
ax2.legend(ncol=3, labels=["adults", "juveniles", "neos"])

# ax2.set_ylim(0,50)

# size = nano[["length_D_adult", "length_D_juvenile", "length_D_neo"]] \
#     .interpolate("time",limit_direction="forward") \
#     .rolling("7d").mean() \

# ax2r = fig.add_subplot(312, sharex=ax2, frameon=False, label="Ds")
# l = ax2r.plot(size.index, size.length_D_adult, "--", label="size")
# ax2r.yaxis.tick_right()
# ax2r.set_ylabel("size")
# ax2r.yaxis.set_label_position("right")
# ax2r.set_ylim(0,100)

algae = nano[["cell_vol_large", "cell_vol_debris"]] \
    .interpolate("time",limit_direction="forward") \
    .rolling("7d").mean()

ax3 = fig.add_subplot(313, sharex=ax1, label="oxy")
ax3.plot(algae["cell_vol_large"], label="cell density")
ax3.plot(algae["cell_vol_debris"], label="debris density")
ax3.legend()
# ax4 = fig.add_subplot(514, sharex=ax1, label="po4")
# ax4.plot(nano.index, nano["NH4"])

fig.autofmt_xdate()

