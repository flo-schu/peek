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

fig, axes = plt.subplots(ncols=10, nrows=8, sharex=True, sharey=True)
axes = axes.flatten()
pdat = d.reset_index()

for ax, i in zip(axes, np.arange(1, 81)):
    dd = pdat.query("id == @i")
    spcs = dd["species"].unique()
    for s in spcs:
        ddd = dd.query("species == @s").reset_index()
        cnt_percent = ddd["count"] / ddd["count"][0]
        ax.plot(ddd["time"], cnt_percent)
        ax.text(0.2, 0.2, str(i), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)        # ax.set_ylabel("Abundance")
        # ax.set_xlabel("Time")
        ax.set_ylim(0,2)
        ax.set_xticks([])
        ax.set_yticks([])

plt.show()
