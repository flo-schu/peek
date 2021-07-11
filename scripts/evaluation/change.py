import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

data = pd.read_csv("data/measurements.csv", infer_datetime_format=True, parse_dates=["time"])
data = data.set_index(["id", "time"]) \
    .sort_index() \
    .query("~ (id == 4 | id == 64)") 


def interpolate(df, cols="all"):
    if cols == "all":
        cols = df.columns
    df = df.loc[:, cols] \
        .reset_index().set_index("time") \
        .groupby("id") \
        .apply(lambda g: g.interpolate("time", limit_direction="forward")) \
        .reset_index().set_index(["id", "time"]) \
        .fillna(0) 

    return df


groups = data.query("time == '2021-06-03'")["esfenvalerate"].values
groups = np.where(groups == 0, 0.01, groups)

orgs = [
    "count_D_adult", "count_D_juvenile", "count_D_neo", 
    "culex_larvae", "culex_small", "culex_pupae", "culex_adults"
]

start = data.query("time == '2021-06-02'")
delay = data.query("time == '2021-07-02'")
change = np.nansum(np.abs(
    (interpolate(delay, orgs).values - interpolate(start, orgs).values) / 
    (interpolate(start, orgs).values + 1)), axis=1)

plt.scatter(groups, change, alpha=.5)
plt.xscale("log")
plt.yscale("log")
plt.ylabel("relative change")
plt.xlabel(r"esfenvalerate concentration [$ng~L^{-1}$]")
plt.xlim(0.005,200)
plt.xticks(ticks=np.unique(groups), labels=["control", 0.1, 1, 10, 100])
plt.savefig("plots/analysis/absolute_relative_change.jpg")

# absolute relatiuve change reveals no changes due to esfenvalerate contamination



# juveniles in relation to esfenvalerate

# plt.scatter(groups, edelay.count_D_juvenile, alpha=.5)

d = interpolate(data, "culex_larvae")
start = d.xs('2021-06-02', level="time").values
delay = d.xs('2021-07-02', level="time").values
food  = data.xs('2021-05-31', level="time")["cell_vol_large"].values
temperature  = data.xs('2021-06-05', level="time")["temperature"].values
sediment = data.xs('2021-05-25', level="time")["sediment_class"].values

sc = plt.scatter(groups, delay - start, alpha=.75, c=sediment, cmap="viridis_r")

lp = lambda i: plt.plot([],color=sc.cmap(sc.norm(i)), mec="none", alpha=.5,
                        label="Feature {:g}".format(i), ls="", marker="o")[0]
handles = [lp(i) for i in np.unique(sediment)]

plt.xscale("log")
plt.xlim(0.005,200)
ticks = plt.xticks(ticks=np.unique(groups), labels=["control", 0.1, 1, 10, 100])
plt.ylabel(r"$\Delta$ culex larvae")
plt.xlabel(r"esfenvalerate concentration [$ng~L^{-1}$]")
plt.legend(handles=handles, labels=["yellow", "green", "other"])
plt.savefig("plots/analysis/change_culex_larvae.jpg")
# plt.yscale("log")

# there seems to be a slight relation between culex development and esfenvalerate application

d = interpolate(data, ["count_D_neo", "count_D_juvenile", "count_D_adult"]).sum(axis=1)
start = d.xs('2021-06-02', level="time").values
delay = d.xs('2021-07-02', level="time").values

plt.scatter(groups, delay - start, alpha=.5)
plt.xscale("log")
plt.xlim(0.005,200)
ticks = plt.xticks(ticks=np.unique(groups), labels=["control", 0.1, 1, 10, 100])
plt.ylabel(r"$\Delta$ Daphnia M.")
plt.xlabel(r"esfenvalerate concentration [$ng~L^{-1}$]")
plt.savefig("plots/analysis/change_daphnia.jpg")