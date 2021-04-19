import os; os.chdir("src")
import pandas as pd
from image.analysis import Data
import evaluation.calc as calc
import evaluation.plot as plot
from matplotlib import pyplot as plt
import itertools as it
import numpy as np

# join all files for analysis
data = Data.combine_data_classic(datapath="../data",
    interpolation_cfg={"method":"pad", "limit":1, "limit_direction":"forward"})
data.fillna(0, inplace=True)

# count organisms per 
# d = calc.count_organisms(data, freq="S", groups=["id","picture", "species", "analysis"])
# get count of organisms for each picture and each analysis
groups = ["id","picture", "species", "analysis","culex_larvae",
          "culex_adults", "culex_pupae", "culex_repro", "sediment"]
d = calc.aggregate(
    data, 
    aggregations={"hash":"size", "value":"mean"}, 
    names=["count", "mean_size"],
    freq="S", groups=groups)

# get sum of analyses for each picture and species
groups=[g for g in groups if g != "analysis"] # remove picture from group list
d = calc.aggregate(
    d, {"count":"sum", "mean_size": "mean"}, names=[],
    freq="S", groups=groups )

# get sum of analyses for each picture and species
groups=[g for g in groups if g != "picture"] # remove picture from group list
d = calc.aggregate(
    d, {"count":"max", "mean_size": "mean"}, names=["count"],
    freq="D", groups=groups )

d.query("id==1")

# plt correlation between image analysis count and manual count
pdat = d.query("species=='Culex'").query("time >= '2021-04-09'").reset_index()
plt.plot(range(-1,26), range(-1,26), color="black")
plt.scatter(pdat["culex_larvae"], pdat["count"])
plt.xlabel("manual count")
plt.ylabel("algorithm count")

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

# plot manual data
# replace algo count on 09.04.2021 with manual count

# plot absolute changes of CUlex and Daphnia


pdat = d.reset_index().query("species == 'Culex'")
pdat["larvae"] = np.where(pdat["time"] == "2021-04-09", pdat["culex_larvae"], pdat["count"])
pdat["larvae"] = np.where(pdat["time"] == "2021-04-16", pdat["culex_larvae"], pdat["count"])
pdat["culex"] = pdat["larvae"] + pdat["culex_adults"] + pdat["culex_pupae"]
# pdat["culex"] = np.where(pdat["id"] == 34, 10, pdat["culex"])
pdat.rename(columns={"culex_adults":"adults", "culex_pupae":"pupae"}, inplace=True)
fig, axes = plt.subplots(ncols=10, nrows=8, sharex=True)
axes = axes.flatten()
for ax, i in zip(axes, np.arange(1, 81)):
    dd = pdat.query("id == @i")
    spcs = dd["species"].unique()
    for s in spcs:
        ddd = dd.query("species == @s").reset_index()
        l, = ax.plot(ddd["time"], ddd["culex"], label="total", color="gray")
        l = ax.fill_between(ddd["time"], [0], ddd["larvae"], alpha=.8, label="larvae")
        l = ax.fill_between(ddd["time"], ddd["larvae"], ddd["larvae"] + ddd["pupae"], alpha=.8, label="pupae")
        l = ax.fill_between(ddd["time"], ddd["larvae"] + ddd["pupae"], ddd["larvae"] + ddd["pupae"] + ddd["adults"], alpha=.8, label="adults")
        ax.axhline(5, 0 , 100, linestyle="--", color="gray", linewidth=.5)
        # ax.set_xlabel("Time")
        ax.set_ylim(0,20)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.text(0.1, 0.8, str(i), horizontalalignment='center', verticalalignment='center', transform=ax.transAxes)        # ax.set_ylabel("Abundance")
        if any(ddd.culex_repro) == True:
            print("repro!")
            plt.setp(ax.spines.values(), color="green")
            plt.setp(ax.texts, color="green")
        elif ddd.culex.to_numpy()[-1] < 5:
            plt.setp(ax.spines.values(), color="red")
            plt.setp(ax.texts, color="red")


fig.subplots_adjust(bottom=0.08, wspace=0.05, hspace=0.05, top=.95, right=0.95, left=0.05)

handles = [axes[2].lines[0]] + axes[2].collections

axes[79].legend(handles = handles, labels=["total", "larvae", "pupae", "adults"], loc='upper right', 
                bbox_to_anchor=(1, -0.05),fancybox=False, shadow=False, ncol=4)
axes[75].set_xlabel("time                         ")
axes[40].set_ylabel("            Abundance of organisms in relation to threshold of critical size (N=5)")
 
plt.show()
