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
        .apply(lambda g: g.interpolate("time", limit_direction="forward", limit=2)) \
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

esfen = data.xs("2021-06-03", level="time")["esfenvalerate"].to_frame()
esfen["esfenvalerate"] = np.where(esfen == 0, 0.01, esfen)
times = np.unique(states.index.get_level_values("time"))
nanos = np.unique(states.index.get_level_values("id"))

# --------------- state development through time -------------------------------

fig = plt.figure()
fig.set_size_inches(10,10)
ax = fig.add_subplot(projection="3d")

def construct_legend(sc, labels):
    cols = np.unique(sc.get_facecolors(), axis=0)
    legend_elements = []
    for c, l in zip(cols, labels):
        line = Line2D([0], [0], color=c, marker="o", alpha=.5, label=l, linestyle="")
        legend_elements.append(line)

    return legend_elements

def init():
    s = states.xs("2021-04-09", level="time")\
        .merge(esfen, how="left", left_index=True, right_index=True) \
        .sort_values("esfenvalerate")

    sc = ax.scatter(s.daphnia, s.culex, s.food_concentration, c=np.log(s.esfenvalerate), s=40)
    ax.set_xlabel("Daphnia abundance")
    ax.set_ylabel("Culex abundance")
    ax.set_zlabel("Food")
    ax.set_zscale("log")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_zlim(0.01, 0.3)
    ax.text(x=1, y=1, z=3, s="2021-04-09", transform=ax.transAxes)
    legend_elements = construct_legend(sc, ["control", 0.1, 1, 10, 100])
    ax.legend(handles=legend_elements, loc='upper right')


def update(t):
    s = states.xs(t, level="time")\
        .merge(esfen, how="left", left_index=True, right_index=True)

    ax.cla()
    sc = ax.scatter(s.daphnia, s.culex, s.food_concentration, c=np.log(s.esfenvalerate), s=40)
    ax.set_xlabel("Daphnia abundance")
    ax.set_ylabel("Culex abundance")
    ax.set_zlabel("Food")
    ax.set_zscale("log")
    ax.set_xlim(0, 100)
    ax.set_ylim(0, 100)
    ax.set_zlim(0.01, 0.3)
    ax.text(x=1, y=1, z=2.5, s=np.datetime_as_string(t, unit="D"), transform=ax.transAxes)
    legend_elements = construct_legend(sc, ["control", 0.1, 1, 10, 100])
    ax.legend(handles=legend_elements, loc='upper right')

ani = FuncAnimation(fig, update, times, init_func=init)

writer = PillowWriter(fps=1)

ani.save("plots/analysis/satespace_animation.gif", writer=writer)

