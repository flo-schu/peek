import sys
from glob import glob
from matplotlib import pyplot as plt
from scipy.signal import find_peaks
from scipy.stats import rv_continuous
import numpy as np
import pandas as pd

sys.path.append("src")
from utils.measurements import CasyFile
from sklearn.metrics import auc

algae = glob("data/raw_measurements/casy_cell_counter/*/*.TXT")

casy_data = [CasyFile(i, correct_dilution=True) for i in algae]

alg_vol_calc = [d.volume_ml_calc for d in casy_data]
alg_vol_casy = [d.volume_ml_casy for d in casy_data]
plt.scatter(alg_vol_calc, alg_vol_casy, alpha=.4)
plt.plot(np.arange(0,3e8, 1e5), np.arange(0,3e8, 1e5))
plt.xlabel("calculated algae volume")
plt.ylabel("casy algae volume")
plt.savefig("plots/algae_measurements.jpg")

kernel = np.ones(9) / 9

algae_data = []

for i in np.arange(len(casy_data)):
    dat = casy_data[i]
    size = dat.size
    # count = dat.data[:, 1]
    count_ml = dat.count_ml
    # difference between data and baseline
    # diffcount = casy_data[i].data[:, 1] - baseline[:, 1]

    # smooth 
    count_convolved = np.convolve(count_ml, kernel, mode='same')
    # exclude first peak
    # data_convolved = np.where(size > 1.8, data_convolved, 0)
    count_convolved = np.where(count_convolved < 0, 0, count_convolved)
    
    # peaks = find_peaks(count_convolved, height=10, distance=10)
    volume = dat.x_volume * count_convolved
    
    debris = np.where(size < 2.5, volume, 0).sum()*10e-12*1000 # ml/L
    large = np.where(size >= 2.5, volume, 0).sum()*10e-12*1000 # ml/L
    ratio = large/debris
    # store data

    algae_data.append([dat.id, dat.date, count_convolved.sum()*1000, volume.sum()*10e-12*1000, debris, large, ratio])
    


colnames = ["msr_id", "time", "cell_count", "cell_volume", "cell_vol_debris", "cell_vol_large", "cell_dl_ratio"]
proc = pd.DataFrame.from_records(algae_data, columns=colnames) 
proc["isid"] = proc["msr_id"].str.isdigit()
data = proc.query("isid") \
    .astype({"msr_id":int}) \
    .sort_values(by=["time","msr_id"]) \
    .drop(columns=["isid"])

data.to_csv("data/measurements/algae.txt", index=False)


# data.query("msr_id == 4")
# casy_data[1462].plot(smoothing_kernel=9)




# from scipy.stats import norm
# from scipy.optimize import minimize
# y = np.convolve(casy_data[1305].count_ml, kernel, mode="same")
# bins = casy_data[1305].size

# # does not work-

# def cell_mix(x, y, bins, p, thresh=1.25):
#     x = np.array(x)
#     N = y.sum()

#     Fragment = norm(loc=p[0], scale=p[1])
#     frags = Fragment.rvs(int(np.round(N * x[0])))
#     counts_fragments = np.digitize(frags, bins=bins)

#     # estimate small cells
#     CellA = norm(loc=p[2], scale=p[3])
#     cells_a = CellA.rvs(int(np.round(N * x[1])))
#     counts_cella = np.digitize(cells_a, bins=bins)

#     # estimate big cells
#     CellB = norm(loc=p[4], scale=p[5])
#     cells_b = CellB.rvs(int(np.round(N * x[2])))
#     counts_cellb = np.digitize(cells_b, bins=bins)

#     # total 
#     cells = np.concatenate([frags, cells_a, cells_b])
#     binned_cells = np.digitize(cells, bins=bins)
#     counts_cells = np.bincount(np.sort(binned_cells))
    
#     ysim = np.zeros(len(y))
#     ysim[:max(binned_cells)+1] = counts_cells

#     ysim = np.where(bins < thresh, 0, ysim)

#     sse = (ysim - y) ** 2 

#     return sse.sum()

# x0 = [.6,.2,.2]
# p=[1.5,0.5,2.75,0.5,4.1,0.5]
# cell_mix(x0, y, bins, p)

# minimize(cell_mix, x0, args = (y, bins, p), bounds=[(0,1)]*3, options={"disp":True})

# # plt.plot(x[:max(counts_fragments)+1], np.bincount(np.sort(counts_fragments)))
# # plt.plot(x[:max(counts_cella)+1], np.bincount(np.sort(counts_cella)))
# # plt.plot(x[:max(counts_cellb)+1], np.bincount(np.sort(counts_cellb)))
# plt.plot(x[:max(counts_cells)+1], np.convolve(np.bincount(np.sort(counts_cells)), kernel, mode="same"))





