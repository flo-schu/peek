import numpy as np
import pandas as pd


def wrangle(df):
    return df.melt(id_vars=["nano_id", "esfenvalerate", "species", "series", "dmso"],
          var_name="time",
          value_name="survival") \
        .assign(time=lambda df: pd.to_datetime(df.time, format="%d.%m.%Y")) \
        .assign(contamination=lambda df: df.time[0]) \
        .assign(time=lambda df: df.time - df.time[0]) \
        .rename(columns={"nano_id":"id"}) \
        .set_index(["id", "time"]).sort_index()

n1 = wrangle(pd.read_csv("data/contamination/20210602_n_series.csv") )
n2 = wrangle(pd.read_csv("data/contamination/20210630_n_series.csv") )
n1_dmso = wrangle(pd.read_csv("data/contamination/20210602_n_series_dmso.csv") )

def wrangle_s(df):
    return df.melt(id_vars=["name", "esfenvalerate", "species", "dmso", "series"],
          var_name="time",
          value_name="survival") \
        .assign(time=lambda df: pd.to_datetime(df.time, format="%d.%m.%Y")) \
        .assign(contamination=lambda df: df.time[0]) \
        .assign(time=lambda df: df.time - df.time[0]) \
        .rename(columns={"name":"id"}) \
        .set_index(["id", "time"]).sort_index()

s1 = wrangle_s(pd.read_csv("data/contamination/20210602_s_series.csv") )
s2 = wrangle_s(pd.read_csv("data/contamination/20210630_s_series.csv") )

def relative_survival(df):
    df = df.reset_index().set_index(["time", "species","id"]).sort_index()
    survival = df.reset_index().set_index(["species", "id"])["survival"].sort_index()
    survival_start = df.xs("0 days", level="time")["survival"].sort_index()
    
    relsurv = pd.DataFrame(survival / survival_start)
    relsurv["time"] = df.reset_index().set_index(["species","id"]).sort_index()["time"].values
    df = df.merge(relsurv.reset_index().set_index(["time","species","id"]), how="left", left_index=True, right_index=True) \
        .rename(columns={"survival_x":"survival","survival_y":"relsurv"})

    return df

n1 = relative_survival(n1).reset_index()
n1_dmso = relative_survival(n1_dmso).reset_index()
n2 = relative_survival(n2).reset_index()
s1 = relative_survival(s1).reset_index()
s2 = relative_survival(s2).reset_index()

data = pd.concat([n1, n1_dmso, n2, s1, s2]) \
    .set_index(["time", "id", "contamination", "series", "species"]) 

data.to_csv("data/measurements/nebenexperiment.csv")

