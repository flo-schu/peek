import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

data = pd.read_csv("data/measurements.csv", infer_datetime_format=True, parse_dates=["time"])
data = data.set_index(["id", "time"]) \
    .sort_index() \
    .query("~ (id == 4)")


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


groups = data.xs("2021-06-03", level="time")["esfenvalerate"].to_frame()
groups["esfenvalerate"] = np.where(groups == 0, 0.01, groups)

orgs = [
    "count_D_adult", "count_D_juvenile", "count_D_neo",
    "culex_larvae", "culex_small", "culex_pupae", "culex_adults"
]


states = interpolate(data, orgs).query("time > '2021-04-06'") \
    .reset_index() \
    .merge(groups, how="left", left_on="id", right_on="id") \
    .assign(culex = lambda df: df.culex_larvae) \
    .assign(daphnia = lambda df: df.count_D_adult + df.count_D_juvenile + df.count_D_neo) \
    .set_index(["time", "id"]) 

    
nanos = np.unique(states.index.get_level_values("id"))

before_conta = states.query("time < '2021-06-03' & time > '2021-05-24'") 
after_conta =  states.query("time > '2021-06-10' & time < '2021-06-24'") 
    

lr_bc = before_conta["culex"].groupby(["id"]).diff().groupby("id").mean()
lr_ac =  after_conta["culex"].groupby(["id"]).diff().groupby("id").mean()

y = (lr_ac-lr_bc)/lr_bc

plt.scatter(groups, y)
# plt.scatter(groups, lr_ac)
plt.xscale("log")
plt.ylim(-30, 30)

from sklearn.linear_model import LinearRegression

lm = LinearRegression(fit_intercept=True)
lm = lm.fit(X=groups.values, y=y.values)

lm.coef_
lm.intercept_