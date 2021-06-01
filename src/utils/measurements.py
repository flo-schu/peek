from matplotlib import pyplot as plt
import numpy as np
from datetime import datetime

class CasyFile:
    def __init__(self, path, splitfile=[28,1052]):
        with open(path, "r") as f:
            raw = f.read().splitlines()
             
        self.meta(data=raw, split=splitfile)
        self.measurements(data=raw, split=splitfile)
        self.calculations(data=raw, split=splitfile)

        print("ID:", self.id, "---", "error:", self.error)

    def meta(self, data, split):
        meta = [i.split("\t") for i in data[:split[0]]]
        
        for m in meta:
            setattr(self, m[0].lower(), m[1])

        self.date = datetime.strptime(self.date, "%d.%m.%y")

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

    def measurements(self, data, split):
        measurements = [i.split("\t") for i in data[split[0]:split[1]]]
        
        self.data = np.array(measurements, dtype=float)

    def plot(self):
        plt.plot(self.data[:, 0], self.data[:, 1])

