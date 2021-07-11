import pandas as pd
from matplotlib import pyplot as plt
from pandas.plotting import register_matplotlib_converters
import numpy as np
import argparse

parser = argparse.ArgumentParser(description="Create animated development of nanos")
parser.add_argument("id", type=str, help="nano ID")
args = parser.parse_args()

register_matplotlib_converters()

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
    return cdat

def plot_lines_and_labels(ax, df, ymax, plot_labels=True, **kwargs):
    events = pd.to_datetime(df.columns, format="%d.%m.%Y")
    ax.vlines(events, 0, 10000, color="black", linestyles="--")
    if plot_labels:
        for x, y, s in zip(
            events.values, 
            np.repeat(ymax/4, len(events.values)), 
            df.values[0] 
            ):
            ax.text(x, y, "{} ng L-1".format(s), rotation="vertical")

nano_id = int(args.id)

data = pd.read_csv("data/measurements.csv", index_col="time", infer_datetime_format=True, parse_dates=["time"])
nano = data.query("id=={}".format(nano_id)).query("time > '2021-04-06'")
contaminations = pd.read_csv("data/contamination/contaminations.csv", infer_datetime_format=True).set_index("id")
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
cumdat = stacked_plot(sdata, ax1, alpha=.6)
ymax = cumdat.iloc[:, -1].max()*1.1
ax1.set_xticks([])
ax1.scatter(nano.index, np.where(nano.culex_repro > 0, 1, np.nan))

ax1.set_ylim(0, ymax)
plot_lines_and_labels(ax1, contaminations.query("id=={}".format(nano_id)), ymax=ymax)
ax1.set_xlim(nano.index.min(), nano.index.max())
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
cumdat = stacked_plot(sdata, ax2, alpha=.6)
ymax = cumdat.iloc[:, -1].max()*1.1
plot_lines_and_labels(ax2, contaminations.query("id=={}".format(nano_id)), ymax=ymax, plot_labels=False)
ax2.set_ylim(0, ymax)
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
ymax = np.nan_to_num(algae.values,0).max() * 1.1
ax3 = fig.add_subplot(313, sharex=ax1, label="oxy")
ax3.plot(algae["cell_vol_large"], label="cells")
ax3.plot(algae["cell_vol_debris"], label="debris")
plot_lines_and_labels(ax3, contaminations.query("id=={}".format(nano_id)), ymax=ymax, plot_labels=False)
ax3.set_ylim(0, ymax)
ax3.set_ylabel("ml L-1")
ax3.legend()


# pc = nano[["oxygen", "pH"]] \
#     .interpolate("time",limit_direction="forward") \
#     .rolling("7d").mean()

# ax4 = fig.add_subplot(414, sharex=ax1, label="other")
# ax4.plot(pc.index, pc["oxygen"])

fig.autofmt_xdate()

plt.savefig("plots/timeseries/{}.jpg".format(nano_id))