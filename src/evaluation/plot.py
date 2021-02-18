import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

class Timeseries:
    def __init__(self, start=0, end=None, df=None):
        self.start = start
        self.end = end
        self.data = self.add_data(df)

    def add_data(self, df):
        pass

    def create(self):
        pass

class Viz:
    @staticmethod
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