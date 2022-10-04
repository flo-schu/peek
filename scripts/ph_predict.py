import sys
import numpy as np
from scipy.optimize import curve_fit
from sklearn.linear_model import LinearRegression
from matplotlib import pyplot as plt
import pandas as pd

def expo_decay_positive(x, k, y_conv):
    return (y_conv- y0) * (1 - np.exp(-k * x)) + y0

data = pd.read_csv("data/raw_measurements/ph/ph_20210504.csv")

est_data = data.iloc[0:3:2,1:].T.values
diff = np.diff(est_data, axis=1)
# y_conv = np.nan_to_num(Y.copy(), 0).max(axis=0)


initialParameters = np.array([1.0, 1.0])
n_fits = data.shape[1]-1

fits = []
for i in range(n_fits):
    if i == 1:
        continue
    d = data.iloc[:, [0, i+1]].dropna(how="any")
    x = d.values[:, 0]
    y = d.values[:, 1]
    y0 = y[0]
    try:
        fit_exp, pcov = curve_fit(expo_decay_positive, x, y, initialParameters)
    except RuntimeError:
        fit_exp = [np.nan, np.nan]
    fits.append(fit_exp)

fits = np.array(fits)

diff = diff[[0]+list(np.arange(2,n_fits))]
lm = LinearRegression(fit_intercept=True)
lm.fit(diff.reshape(diff.shape), fits[:,0])
plt.plot(diff, fits[:,0], "o")
xmod = np.linspace(0,1, 100).reshape(100, 1)
plt.plot(xmod, lm.predict(xmod))
plt.xlim(0, 0.2)
plt.ylim(0, 2)
plt.xlabel("2 minute difference in pH")
plt.ylabel("fitted parameter")
print("slope:",lm.coef_)
print("intercept:",lm.intercept_)

