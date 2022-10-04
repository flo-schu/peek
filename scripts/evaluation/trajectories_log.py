import pandas as pd
from matplotlib import pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation, PillowWriter  
from matplotlib.cm import get_cmap
from matplotlib.lines import Line2D


data = pd.read_csv("data/measurements.csv", infer_datetime_format=True, parse_dates=["time"])
data = data.set_index(["id", "time"]) \
    .sort_index() 




def interpolate(df, cols="all"):
    if cols == "all":
        cols = df.columns
    df = df.loc[:, cols] \
        .reset_index().set_index("time") \
        .groupby("id") \
        .apply(lambda g: g.interpolate("time", limit_direction="forward", limit=1)) \
        .reset_index().set_index(["id", "time"]) \
        .fillna(0) 

    return df


statevars = [
    "count_D_adult", "count_D_juvenile", "count_D_neo", 
    "culex_larvae", "culex_small", "culex_pupae", "culex_adults",
    "cell_vol_large", "oxygen"
]

states = interpolate(data, statevars).query("time > '2021-04-06'") \
    .assign(culex = lambda df: df.culex_larvae) \
    .assign(daphnia = lambda df: df.count_D_adult + df.count_D_juvenile + df.count_D_neo) \
    .rename(columns={"cell_vol_large":"food_concentration"}) \
    .loc[:, ["culex", "daphnia", "food_concentration", "oxygen"]]

svars = states.columns

# prepare data
esfen = data.xs("2021-06-03", level="time")["esfenvalerate"].to_frame()
esfen["esfenvalerate"] = np.where(esfen == 0, 0.01, esfen)
times = np.unique(states.index.get_level_values("time"))
nanos = np.unique(states.index.get_level_values("id"))

estates = states.replace(0, 0.1) \
    .reset_index() \
    .merge(esfen, how="left", left_on="id", right_on="id") \
    .set_index(["time","id"]) 

# log statespace with trajectories ---------------------------------------------


# select colors and contruct legend
cmap = get_cmap("viridis")
colors = cmap(np.linspace(0,1, 5))
esf = pd.DataFrame([
    [0.01, 0.1, 1, 10, 100],
    colors,
    ["control", 0.1, 1, 10, 100]
]).T.rename(columns={0:"esfenvalerate", 1:"color", 2:"label"})

legend_elements = []
for c, l in zip(esf.color, esf.label):
    line = Line2D([0], [0], color=c, marker="o", alpha=.5, label=l, linestyle="", linewidth=.5)
    legend_elements.append(line)

legend_elements.append(Line2D([0],[0], color="black", marker="o", linestyle="", label="reference", linewidth=.5, alpha=.5))

# plot state before contamination
precon = estates.query("time < '2021-06-03'")

fig = plt.figure()
fig.set_size_inches(10,10)

ax = fig.add_subplot()
ax.legend(handles=legend_elements, loc="upper left")

ax.plot(precon.daphnia, precon.culex, marker="o", color="black", alpha=.2, linewidth=.5, linestyle="")
ax.set_xscale("log")
ax.set_yscale("log")
ax.set_ylim(0.05, 300)
ax.set_xlim(0.05, 300)
ax.set_xlabel("Daphnia abundance")
ax.set_ylabel("Culex abundance")

# plot state after contamination

postcon = estates.query("time >= '2021-06-03'")
for name, group in postcon.groupby("esfenvalerate"):
    t = esf.query("esfenvalerate=={}".format(name))
    ax.plot(group.daphnia, group.culex, color=t.color.values[0], 
             marker="o", linewidth=.5, linestyle="", alpha=.2)


plt.savefig("plots/analysis/state_space_deviations.jpg", dpi=200)


# plot state before contamination
precon = estates.query("time < '2021-06-03'")
postcon = estates.query("time >= '2021-06-03'")


for name, group in postcon.groupby("esfenvalerate"):
    t = esf.query("esfenvalerate=={}".format(name))
    legend_elements = [
        Line2D([0], [0], color=t.color.values[0], marker="o", alpha=.5, 
               label=t.label.values[0], linestyle="", linewidth=.5),
        Line2D([0], [0], color="black", marker="o", alpha=.5, label="reference", 
               linestyle="", linewidth=.5)
    ]

    fig = plt.figure()
    fig.set_size_inches(10,10)

    ax = fig.add_subplot()
    ax.legend(handles=legend_elements, loc="upper left")
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_ylim(0.05, 300)
    ax.set_xlim(0.05, 300)
    ax.set_xlabel("Daphnia abundance")
    ax.set_ylabel("Culex abundance")

    ax.plot(precon.daphnia, precon.culex, marker="o", color="black", 
            alpha=.2, linewidth=.5, linestyle="")

    ax.plot(group.daphnia, group.culex, color=t.color.values[0], 
             marker="o", linewidth=.5, linestyle="", alpha=.5)



    plt.savefig("plots/analysis/state_space_deviations_{}.jpg".format(name), dpi=200)
    plt.close()
# plot state after contamination

