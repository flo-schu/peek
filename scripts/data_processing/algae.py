import sys
from glob import glob
from matplotlib import pyplot as plt
from scipy.signal import find_peaks
import numpy as np
import pandas as pd

sys.path.append("src")
from utils.measurements import CasyFile
from sklearn.metrics import auc

algae = glob("data/raw_measurements/casy_cell_counter/*/*.TXT")

casy_data = [CasyFile(i) for i in algae]

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
    
    # store data

    algae_data.append([dat.id, dat.date, count_convolved.sum(), volume.sum()])
    
    # plot
    # fig, ax = plt.subplots(1, 1)
    # ax.plot(size, data_convolved)
    # plt.savefig("plots/algae/" + data[i].date.strftime("%Y%m%d_") + data[i].id + data[i].error + ".jpg")
    # plt.close()




colnames = ["msr_id", "time", "algae_count", "algae_volume"]
proc = pd.DataFrame.from_records(algae_data, columns=colnames) 
proc["isid"] = proc["msr_id"].str.isdigit()
data = proc.query("isid") \
    .astype({"msr_id":int}) \
    .sort_values(by=["time","msr_id"]) \
    .drop(columns=["isid"])

data.to_csv("data/measurements/algae.txt", index=False)