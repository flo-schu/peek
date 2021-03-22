import pandas as pd
from evaluation.calc import Algorithms as algs
from matplotlib import pyplot as plt
import numpy as np

def show_ts(ts_data):
    ax = plt.subplot()
    for i in ts_data.index.levels[1]:
        ax.plot(ts_data.xs(i, level = "id"), color="grey")
    ax.set_xlabel("time")
    ax.set_ylabel("n organisms")
    plt.show()

def color_analysis(img, channel="r"):
    if channel == "r" or channel == "red":
        c = 0
    elif channel == "g" or channel == "green":
        c = 1
    elif channel == "b" or channel == "blue":
        c = 2
    else: 
        print("wrong channel spec. Please use 'r', 'g', or 'b'.")
        return
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
    ax1.imshow(np.rot90(img))
    ax2.imshow(np.rot90(img[:, :, c]), cmap="Greys_r")
    ax3.plot(img[:,:,c], color= channel, alpha= .05)
    ax3.plot(img[:,:,c].min(axis=1), color = "black")
    ax3.plot(img[:,:,c].max(axis=1), color = "black")
    ax3.set_ylim(0,255)

class Viz:
    @staticmethod
    def color_analysis(img, channel="r"):
        color_analysis(img, channel)

    @staticmethod
    def show_ts(ts_data):
        show_ts(ts_data)