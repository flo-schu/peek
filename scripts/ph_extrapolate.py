import os
import sys
import numpy as np
from scipy.optimize import curve_fit
from matplotlib import pyplot as plt
import pandas as pd
import argparse

def expo_decay_positive(x, k, y_conv):
    return (y_conv- y0) * (1 - np.exp(-k * x)) + y0

def logartihmic(x, a, b): # x-shifted log
    return a * np.log(x + b) + y0

nano = sys.argv[1]
raw = pd.read_csv("data/raw_measurements/ph/ph_20210504.csv")
data = raw[["t", nano]].dropna(how="any")
x = data.values[:, 0]
y = data.values[:, 1]
y0 = y[0]

initialParameters = np.array([1.0, 1.0])

fit_log, pcov = curve_fit(logartihmic, x, y, initialParameters)
modelPredictions = logartihmic(x, *fit_log) 

fit_exp, pcov = curve_fit(expo_decay_positive, x, y, initialParameters)
modelPredictions = expo_decay_positive(x, *fit_exp) 

absError = modelPredictions - y
SE = np.square(absError) # squared errors
MSE = np.mean(SE) # mean squared errors
RMSE = np.sqrt(MSE) # Root Mean Squared Error, RMSE
Rsquared = 1.0 - (np.var(absError) / np.var(y))

absError = modelPredictions - y
SE = np.square(absError) # squared errors
MSE = np.mean(SE) # mean squared errors
RMSE = np.sqrt(MSE) # Root Mean Squared Error, RMSE
Rsquared = 1.0 - (np.var(absError) / np.var(y))

# print("================================================")
# print("logarithmic model")
# print('Parameters:', fit_log)
# print('RMSE:', RMSE)
# print('R-squared:', Rsquared)
print("================================================")
print("pH curve for Nano", nano)
print("positive exponential decay model")
print('Parameters:', y0, fit_exp)
print('RMSE:', RMSE)
print('R-squared:', Rsquared)
print("================================================")


plt.plot(x, y, "o", alpha =.7)
xmod = np.linspace(0, 30, num=100)
ymod_l = logartihmic(xmod, *fit_log)
ymod_e = expo_decay_positive(xmod, *fit_exp)
plt.xlabel("time [minutes]")
plt.ylabel("pH")
# plt.plot(xmod, ymod_l, label="logarithmic")
plt.plot(xmod, ymod_e, label="positive exponential decay")
plt.legend()
plt.show()
