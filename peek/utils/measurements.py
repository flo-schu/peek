from matplotlib import pyplot as plt
import numpy as np
from datetime import datetime

class CasyFile:
    def __init__(self, path, splitfile=[28,1052], correct_dilution=False, verbose=False):
        with open(path, "r") as f:
            raw = f.read().splitlines()
             
        self.meta(data=raw, split=splitfile)
        self.measurements(data=raw, split=splitfile)
        self.calculations(data=raw, split=splitfile)
        if correct_dilution:
            self.correct_dilution()
        self.count_ml = self.dilution_to_ml(self.data[:, 1])
        self.recalculate()

        if verbose:
            print("ID:", self.id, "---", "error:", self.error)

    def meta(self, data, split):
        meta = [i.split("\t") for i in data[:split[0]]]
        
        for m in meta:
            setattr(self, m[0].lower(), m[1])

        self.dilution = float(self.dilution.replace(" ",""))
        self.sample_volume = float(self.__dict__.pop("sample volume (µl)"))
        self.cycles = int(self.__dict__.pop("cycles"))
        self.date = datetime.strptime(self.date, "%d.%m.%y")
        self.volume_correction = float(self.__dict__.pop("volume correction").replace(" ",""))

        comment = getattr(self, "comment 1").split("_")
        
        try:
            self.id = comment[1].replace("^", "")
        except IndexError:
            self.id = "None"

        try:
            self.error = comment[2]
            if self.error == "ADAM":
                self.id += "_ADAM"
                try:
                    self.error = comment[3]
                except IndexError:
                    self.error = "None"
        except IndexError:
            self.error = "None"

    def calculations(self, data, split):
        calculations = [i.split("\t") for i in data[split[1]:]]
        
        for c in calculations:
            setattr(self, c[0], c[1])

        self.volume_ml_casy = float(self.__dict__.pop("Volume/ml"))
        self.counts_ml_casy = float(self.__dict__.pop("Counts/ml"))

    def measurements(self, data, split):
        measurements = [i.split("\t") for i in data[split[0]:split[1]]]
        
        self.data = np.array(measurements, dtype=float)
        self.size = self.data[:, 0]

    def plot(self, smoothing_kernel=1):
        kernel = np.ones(smoothing_kernel) / smoothing_kernel
        count_convolved = np.convolve(self.data[:, 1], kernel, mode='same')

        plt.plot(self.data[:, 0], count_convolved)
        plt.vlines(x=2.5,ymin=0,ymax=max(count_convolved), linestyles="--")

    def correct_dilution(self):
        self.counts_ml_casy /= self.dilution
        self.volume_ml_casy /= self.dilution

        if self.dilution == 110:
            self.dilution = 11 / 1
        if self.dilution == 103:
            self.dilution = 5.15 / 0.15
        if self.dilution == 101:
            self.dilution = 10.1 / 0.1

        self.counts_ml_casy *= self.dilution
        self.volume_ml_casy *= self.dilution

    def dilution_to_ml(self, a):
        """
        a:          list or array like structure
        
        sample_vol: sampled volume in µL

        returns:    a rescaled to per mL values
        """
        a = np.array(a)
        sampled_medium = self.sample_volume * self.cycles
        return a / sampled_medium * 1000 * self.dilution / self.volume_correction


    def recalculate(self):
        self.x_volume = 4/3 * np.pi * (self.data[:, 0] / 2) ** 3 
        self.volume_ml_calc = (self.x_volume * self.count_ml).sum()
        self.counts_ml_calc = self.count_ml.sum()
