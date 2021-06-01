import sys
from glob import glob
from matplotlib import pyplot as plt
from scipy.signal import find_peaks
import numpy as np
import pandas as pd

sys.path.append("src")
from utils.measurements import CasyFile
from sklearn.metrics import auc

algae = glob("data/raw_measurements/casy_cell_counter/20210524001/*.TXT")

data = [CasyFile(i) for i in algae]


baseline = data[2].data
size = baseline[:, 0]
kernel = np.ones(9) / 9


algae_data = []

for i in np.arange(3, len(data)):
    
    # difference between data and baseline
    diffcount = data[i].data[:, 1] - baseline[:, 1]

    # smooth 
    data_convolved = np.convolve(diffcount, kernel, mode='same')

    # exclude first peak
    data_convolved = np.where(size > 1.8, data_convolved, 0)
    data_convolved = np.where(data_convolved < 0, 0, data_convolved)
    
    # peaks = find_peaks(data_convolved, height=10, distance=10)
    area = auc(size, data_convolved)
    
    # store data
    algae_data.append([data[i].id, data[i].date, area])
    
    # plot
    # fig, ax = plt.subplots(1, 1)
    # ax.plot(size, data_convolved)
    # plt.savefig("plots/algae/" + data[i].date.strftime("%Y%m%d_") + data[i].id + data[i].error + ".jpg")
    # plt.close()


processed_data = pd.DataFrame.from_records(algae_data, columns=["msr_id", "time", "algae_signal"]) 

processed_data.to_csv("data/measurements/algae.txt", index=False)