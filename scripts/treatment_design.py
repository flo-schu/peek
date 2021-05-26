import pandas as pd
from sklearn import preprocessing
import numpy as np
from progress.bar import Bar
from matplotlib import pyplot as plt

rawdata = pd.read_csv("data/grouping.csv")

optimize_columns = ["culex", "radiation", "mdTemp", "conductivity", "oxygen", "pH", "position", "sediment_class"]
n_groups = 5
groups = rawdata["Gruppe"].values

# scale the data
dataoptim = rawdata[optimize_columns].values
scaler = preprocessing.StandardScaler().fit(dataoptim)

data = scaler.transform(dataoptim)


def balance(data, groups):
    X_mean = []
    for g in np.arange(1, n_groups+1):
        x = data[np.where(groups == g)[0],:]
        # take mean along sample axis
        x_mean = x.mean(axis=0)
        X_mean.append(x_mean)

    return np.sum(np.array(X_mean)**2)


def switch(groups):
    sgroups = groups.copy()
    switched = np.random.randint(0,79, 2)
    sgroups[switched] = groups[switched[::-1]]

    while np.sum((sgroups - groups)**2) == 0:
        sgroups = switch(groups)

    return sgroups

def step(data, groups):
    x0 = balance(data, groups)
    switched_groups = switch(groups)
    x1 = balance(data, switched_groups)
    
    if x1 - x0 < 0:
        return (1, switched_groups, x1)
    else:
        return (0, groups, x0)


def optimize(data, groups, iterations=10000):
    bar = Bar("optimizing", max=iterations)

    for i in range(iterations):
        res = step(data, groups)
        accept = res[0]
        new_groups = res[1]
        ssqerr = res[2]
        
        if accept:
            print("accepted:", ssqerr, accept)
            groups = new_groups

        bar.next()

    bar.finish()

    return groups

def plot(df, columns, groups="groups"):
    gdf = df.groupby(groups)
    for c in columns:
        gdf.boxplot(column=c, layout=(1,5))
        plt.savefig("plots/groups/" + c + ".jpg")

optimized_groups = optimize(data, groups)

rawdata["groups"] = optimized_groups
plot(rawdata, optimize_columns)

plot(rawdata, ["NO2","NO3","NH4","PO4","culex_larvae","culex_add","D_add","headspace","sed_h","turbidity"])

# show mean values
rawdata.groupby("groups").gdata.mean()


rawdata.to_csv("data/groups_optimized.csv", index=False)