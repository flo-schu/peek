import sys
from glob import glob
from matplotlib import pyplot as plt
sys.path.append("src")
from utils.measurements import CasyFile

algae = glob("data/raw_measurements/casy_cell_counter/20210427001/*.TXT")

data = [CasyFile(i) for i in algae]


baseline = data[1]
for i in data:
    fig, (ax1, ax2) = plt.subplots(2, 1)
    ax1.plot(baseline.data[:, 0], baseline.data[:, 1])
    ax1.plot(i.data[:, 0], i.data[:, 1])
    diffcount = i.data[:, 1] - baseline.data[:, 1]
    ax2.plot(i.data[:, 0], diffcount)
    plt.savefig("plots/algae/" + i.date.strftime("%Y%m%d_") + i.id + i.error + ".jpg")
    plt.close()