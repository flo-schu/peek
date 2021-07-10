import pandas as pd
from sklearn import preprocessing
import numpy as np
from progress.bar import Bar
from matplotlib import pyplot as plt

def balance(data, groups, weights):
    X_mean = []
    levels = list(np.unique(groups))
    for l in levels:
        x = data[np.where(groups == l)[0],:]
        # take mean along sample axis
        x_mean = x.mean(axis=0) * weights
        X_mean.append(x_mean)

    return np.sum(np.array(X_mean)**2)


def switch(groups, n):
    sgroups = groups.copy()
    switched = np.random.choice(np.arange(len(groups)), n, replace=False).astype(int)
    if n == 2:
        sgroups[switched] = groups[switched[::-1]]
    else:
        scramble = np.random.choice(switched, n, replace=False)
        sgroups[switched] = groups[scramble]

    while all(sgroups == groups):
        sgroups = switch(groups, n)

    return sgroups

def step(data, groups, switch_n, weights):
    x0 = balance(data, groups, weights)
    switched_groups = switch(groups, switch_n)
    x1 = balance(data, switched_groups, weights)
    
    if x1 - x0 < 0:
        return (1, switched_groups, x1)
    else:
        return (0, groups, x0)

def optimize(data, groups, switch_n=2, iterations=10000, weights=None, **kwargs):
    bar = Bar("optimizing", max=iterations)

    for i in range(iterations):
        res = step(data, groups, switch_n, weights)
        accept = res[0]
        new_groups = res[1]
        ssqerr = res[2]
        
        conditions = nebenbedingungen(new_groups, rawdata, **kwargs)

        if accept and conditions:
            print("accepted:", ssqerr, accept)
            groups = new_groups
            ssqerr_min = ssqerr
        bar.next()

    bar.finish()

    return groups, ssqerr_min

def plot(df, columns, groups="groups"):
    gdf = df.groupby(groups)
    for c in columns:
        gdf.boxplot(column=c, layout=(1,6))
        plt.savefig("plots/groups/5/" + c + ".jpg")
        plt.close()

def nebenbedingungen(groups, rawdata):
    for i in list(np.unique(groups)):
        ids_in_group = rawdata.iloc[groups==i].id.to_numpy()
        status_in_group = rawdata.iloc[groups==i].status.to_numpy()
        
        id_trueb = [4, 15, 64]
        id_white = [15, 17]

        if np.sum([i in ids_in_group for i in id_trueb]) > 1:
            return False

        if np.sum([i in ids_in_group for i in id_white]) > 1:
            return False

        if np.sum(np.where(status_in_group == 1, 1, 0)) < 3:
            return False

        return True

rawdata = pd.read_csv("data/groups/input_data.csv")
rawdata["culex"] = rawdata["culex_small"] + rawdata["culex_larvae"]
optimize_columns = ["culex_larvae", "culex_small","radiation", "midday_temperature", "conductivity", "pH", "position", "sediment_class", "status", "daphnia_count", "algae_signal", "oxygen"]
weights = np.array([1,1,1,1,1,1,1,1,1,1,1,1])
# nebenbedingungen

# before optimizing. Make sure no extreme outliers are in the data. 
# Because the optimizatin process is highly sensitive to those values 
# because it always takes the mean. A good practice is to reduce outliers to 
# similar high values. Thus they have an appropriate influence on the optimization
# but won't bias the procedure

# scale the data
dataoptim = rawdata[optimize_columns].values
scaler = preprocessing.StandardScaler().fit(dataoptim)

data = scaler.transform(dataoptim)

groups_5 = [1,2,3,4,5]
n_groups_5 = [16,16,16,16,16]

optim_groups = []
for i in range(5):
    groups = np.random.choice(np.repeat(groups_5, n_groups_5), 80, replace=False)
    while not nebenbedingungen(groups, rawdata):
        groups = np.random.choice(np.repeat(groups_5, n_groups_5), 80, replace=False)
    og = optimize(data, groups, switch_n=2, iterations=20000, weights=weights, rawdata=rawdata)
    optim_groups.append(og)
    rawdata["groups_"+str(i)+"_"+str(round(og[1],2))] = og[0]



# save output and new groups
rawdata.to_csv("data/groups/groups_optimized.csv", index=False)

# groups=pd.read_clipboard()
# rawdata=pd.concat([rawdata, groups], axis=1)
# plot data

# rawdata = pd.read_csv("data/groups/groups_optimized.csv")

plot(rawdata, optimize_columns, groups="groups_1_0.09")
plot(rawdata, ["NO2","NO3","NH4","PO4","culex_larvae","culex_add","daphnia_add","headspace","sediment_height","turbidity", "algae_signal", "culex_adults"], groups="groups_1_0.09")
# show mean values

