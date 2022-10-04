import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
from matplotlib.lines import Line2D
from scipy.optimize import curve_fit


def logistic_3par(xdata, baserate, slope, loc):
    return ((baserate-0)/(1.0+((xdata/loc)**slope))) + 0
 
data = pd.read_csv("data/measurements/nebenexperiment.csv") \
    .assign(esfenvalerate=lambda df: np.where(df.esfenvalerate == 0, 0.01, df.esfenvalerate)) \
    .assign(contamination=lambda df: np.where(df.contamination == "2021-06-05", "2021-06-03", df.contamination)) \
    .set_index(["contamination", "series", "species","time", "id"]) \
    .query("dmso == 1")

series = np.unique(data.index.get_level_values("series"))
contamination = np.unique(data.index.get_level_values("contamination"))
species = np.unique(data.index.get_level_values("species"))
xpred = np.logspace(-2, 3, num=100)


fig, (ax1, ax2) = plt.subplots(ncols=1, nrows=2, sharex=True)
fig.set_size_inches(10,5)

for s, facecolor, linestyle in zip(series, ["blue", "None"], ["-","--"]):
    for c, marker in zip(contamination, ["o", "^"]):
        for sp, ax in zip(species, [ax1, ax2]):
            d = data.xs((s, c, "6 days", sp), level=("series", "contamination", "time", "species"))
            dg = d.groupby("esfenvalerate").mean()
            
            (baserate, slope, loc), _ = curve_fit(
                logistic_3par, 
                xdata=np.concatenate([d.esfenvalerate.values, np.repeat([1000],10)]), 
                ydata=np.concatenate([d.relsurv.values, np.repeat([0],10)]))
            ypred = logistic_3par(xpred, baserate, slope, loc)

            sc = ax.scatter(dg.index, dg.relsurv, marker=marker, color=facecolor, edgecolors="blue", alpha=.5)
            li = ax.plot(xpred, ypred, color="black", linestyle=linestyle, linewidth=1)
            
            ax.set_xscale("log")
            ax.set_xlim(0.005, 2000)


ax1.text(0.02, 0.1, species[0], verticalalignment='center', transform=ax1.transAxes)
ax2.text(0.02, 0.1, species[1], verticalalignment='center', transform=ax2.transAxes)

ticks = ax2.set_xticks(dg.index)
labels = ax2.set_xticklabels(labels=["DMSO", 0.1, 1, 10, 100, 1000])

legend_elements = [
    Line2D([0], [0], color='None', markeredgecolor='blue', marker="o", alpha=.5, label='ADAM medium'),
    Line2D([0], [0], color='blue', markeredgecolor='blue', linestyle="", marker="o", alpha=.5, label='Nanocosm medium'),
    Line2D([0], [0], color='None', markeredgecolor='blue', marker="o", label='1st contamination'),
    Line2D([0], [0], color='None', markeredgecolor='blue', marker="^", label='2nd contamination'),
]
ax1.legend(handles=legend_elements, loc='upper right')

plt.savefig("plots/analysis/nebenexperiment.jpg", dpi = 100)




# in the first contamination, 10 fold higher DMSO concentration was used
# in ADAM medium. This 