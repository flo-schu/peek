import os; os.chdir("src")
import pandas as pd
from image.analysis import Data
import evaluation.calc as calc
import evaluation.plot as plot
from matplotlib import pyplot as plt
import numpy as np

# join all files for analysis
data = Data.combine_data_classic()

# count organisms per 
# d = calc.count_organisms(data, freq="S", groups=["id","picture", "species", "analysis"])

# get count of organisms for each picture and each analysis
d = calc.aggregate(
    data, {"hash":"size", "value":"mean"}, names=["count", "mean_size"],
    freq="S", groups=["id","picture", "species", "analysis"] )

# get sum of analyses for each picture and species
d = calc.aggregate(
    d, {"count":"sum", "mean_size": "mean"}, names=[],
    freq="S", groups=["id","picture", "species"] )

# get sum of analyses for each picture and species
d = calc.aggregate(
    d, {"count":"max", "mean_size": "mean"}, names=["count"],
    freq="D", groups=["id", "species"] )

# plot.show_ts_classes(d.query("id==1"), classcol="species", value="mean_size")


# plot relative changes of CUlex and Daphnia
fig, axes = plt.subplots(ncols=10, nrows=8, sharex=True, sharey=True)
axes = axes.flatten()
pdat = d.reset_index()
lines = []
for ax, i in zip(axes, np.arange(1, 81)):
    dd = pdat.query("id == @i")
    spcs = dd["species"].unique()
    for s in spcs:
        ddd = dd.query("species == @s").reset_index()
        cnt_percent = ddd["count"] / ddd["count"][0]
        l, = ax.plot(ddd["time"], cnt_percent, label = s)
        ax.text(0.2, 0.2, str(i), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)        # ax.set_ylabel("Abundance")
        # ax.set_xlabel("Time")
        ax.set_ylim(0,2)
        ax.set_xticks([])
        ax.set_yticks([])
        lines.append(l)

fig.subplots_adjust(bottom=0.08, wspace=0.05, hspace=0.05, top=.95, right=0.95, left=0.05)

axes[79].legend(handles = lines[:2], labels=list(spcs), loc='upper right', 
                bbox_to_anchor=(1, -0.05),fancybox=False, shadow=False, ncol=2)
axes[75].set_xlabel("time                      ")
axes[40].set_ylabel("               relative change in Abundance of Organisms")

plt.show()





# plot absolute changes of CUlex and Daphnia
fig, axes = plt.subplots(ncols=10, nrows=8, sharex=True)
axes = axes.flatten()
pdat = d.reset_index().query("species == 'Culex'")
lines = []
for ax, i in zip(axes, np.arange(1, 81)):
    dd = pdat.query("id == @i")
    spcs = dd["species"].unique()
    for s in spcs:
        ddd = dd.query("species == @s").reset_index()
        l, = ax.plot(ddd["time"], ddd["count"], label = s)
        ax.axhline(5, 0 , 100, linestyle="--", color="black")
        ax.text(0.1, 0.8, str(i), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)        # ax.set_ylabel("Abundance")
        # ax.set_xlabel("Time")
        ax.set_ylim(0,20)
        ax.set_xticks([])
        ax.set_yticks([])
        lines.append(l)

fig.subplots_adjust(bottom=0.08, wspace=0.05, hspace=0.05, top=.95, right=0.95, left=0.05)

axes[79].legend(handles = lines[:2], labels=list(spcs), loc='upper right', 
                bbox_to_anchor=(1, -0.05),fancybox=False, shadow=False, ncol=2)
axes[75].set_xlabel("time                         ")
axes[40].set_ylabel("            Abundance of organisms in relation to threshold of critical size (N=5)")
 
plt.show()