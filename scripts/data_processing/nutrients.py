import sys
from glob import glob
import pandas as pd
import numpy as np
from matplotlib import pyplot as plt
sys.path.append("src")
from image.analysis import Data
        
# in preparation only the first row (column names) of the files need to be 
# modified: Change Verdünnung to Verduennung. Then no key errors will occurr.

# load data
df = Data.read_csv_list(glob("data/raw_measurements/nutrients_photometer_mn/*.csv"))
df.dropna(how="all", inplace=True) # drop rows if all values are NA

# create time column from sample date
df['time'] = pd.to_datetime(df['SampleDate'], format="%d.%m.%Y")

# rename and drop unnecessary columns 
df = df.drop(columns=[
    "Verduennung","STAT","TYPE","Computer", "Anwender",  
    "send", "Dezimalen", "Datum", "Zeit", 
    "Probenort", "Methodennummer", "SampleDate"
    ])


# unite Ammonium 15 and Ammonium 3 methods
# df["Methodenname"] = np.where(
#     (df["Methodenname"] == "AMMONIUM 15") | (df["Methodenname"] == "AMMONIUM 3"),
#     "AMMONIUM",
#     df["Methodenname"]
# )

# create msr_id from Zaheler column
df = df.sort_values(["time","Zaehler"])
df['msr_id'] = df.groupby(["time","Methodenname"]).cumcount()+1

# extract nutrient
df['nutrient'] = ["".join(s.split("mg/L ")[1].split(" ")) for s in list(df["Einheit"])]

# df export turbidity data (take mean from all measurements)
df.rename(columns={"NTU":"turbidity", "A": "absorption"}, inplace=True)
turbidity = df[["time","msr_id","turbidity"]]
turbidity = turbidity.groupby(["time","msr_id"]).mean().reset_index()

# join measured and estimated concentration columns
df["concentration"] = np.where(pd.isna(df.Bemerkung), df["Messwert"], df["EST"])

# drop additional columns
df.drop(columns=["Zaehler", "Messwert", "Bemerkung", "EST", "turbidity", "Einheit"], inplace=True)

# drop ammonoum 3 measurements
df = df.query("Methodenname != 'AMMONIUM 3'")

# drop measurements of NH3 (these could be included later on if this can be done by calculation)
df = df.query("nutrient != 'NH3'")

concentration = df.pivot(
    index=["time","msr_id"], 
    columns=["nutrient"], 
    values=["concentration"]
    ).reset_index()

concentration = Data.flatten_columns_and_replace(concentration, "concentration","")

absorption = df.pivot(
    index=["time","msr_id"], 
    columns=["nutrient"], 
    values=["absorption"]
    ).reset_index()

absorption = Data.flatten_columns_and_replace(absorption, "absorption", "")

from sklearn.linear_model import LinearRegression
def estimate_concentration(x, y, include_zeros=True):
    yorig = y
    xorig = x
    d = np.array([x, y])

    # remove NAs rowwise
    d = d[:, ~np.isnan(d).any(axis = 0)].T
    if include_zeros:
        pass
    else:
        d = d[d[:, 1] > 0, :]
    x = d[:, 0].reshape( d.shape[0],1)
    y = d[:, 1]

    # fit model
    lm = LinearRegression(fit_intercept=True)
    lm.fit(x, y)

    # estimate and replace negative values with zeros
    result = lm.coef_ * xorig + lm.intercept_
    result = np.where(result < 0, 0, result)
    
    return result

fig, ax = plt.subplots(1,1)
nut = "NO2" # nitrite
est = estimate_concentration(absorption[nut], concentration[nut])
ax.plot(absorption[nut], est, "o", color="black", alpha=.5)
ax.plot(absorption[nut], concentration[nut], 'go', alpha=.1)
ax.set_xlabel("Absorption")
ax.set_ylabel("Concentration [mg L-1]")
plt.savefig("plots/nutrient_estimation_nitrite.jpeg")
concentration["NO2"] = est

fig, ax = plt.subplots(1,1)
nut = "NO3"
est = estimate_concentration(absorption[nut], concentration[nut])
ax.plot(absorption[nut], est, "o", color="black", alpha=.5)
ax.plot(absorption[nut], concentration[nut], 'go', alpha=.5)
ax.set_xlabel("Absorption")
ax.set_ylabel("Concentration [mg L-1]")
plt.savefig("plots/nutrient_estimation_nitrate.jpeg")
concentration["NO3"] = est

fig, ax = plt.subplots(1,1)
nut = "PO4"
est = estimate_concentration(absorption[nut], concentration[nut])
ax.plot(absorption[nut], est, "o", color="black", alpha=.5)
ax.plot(absorption[nut], concentration[nut], 'go', alpha=.5)
ax.set_xlabel("Absorption")
ax.set_ylabel("Concentration [mg L-1]")
plt.savefig("plots/nutrient_estimation_phosphate.jpeg")
concentration["PO4"] = est

fig, ax = plt.subplots(1,1)
nut = "NH4"
est = estimate_concentration(absorption[nut], concentration[nut], include_zeros=False)
ax.plot(absorption[nut], est, "o", color="black", alpha=.5)
ax.plot(absorption[nut], concentration[nut], 'go', alpha=.5)
ax.set_xlabel("Absorption")
ax.set_ylabel("Concentration [mg L-1]")
plt.savefig("plots/nutrient_estimation_ammonium.jpeg")
concentration["NH4"] = est

turbidity.to_csv("data/measurements/turbidity.txt", index=False)
concentration.to_csv("data/measurements/nutrients.txt", index=False)
