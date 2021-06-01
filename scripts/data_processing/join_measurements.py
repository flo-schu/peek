import pandas as pd
import sys
from datetime import datetime
sys.path.append("src")
from image.analysis import Data

# load data matched by measurement id to nano id
match = pd.read_csv("data/measurements/match.txt")
temperature =  pd.read_csv("data/measurements/temperature.txt")
oxygen =  pd.read_csv("data/measurements/oxygen.txt")
nutrients =  pd.read_csv("data/measurements/nutrients.txt")
turbidity =  pd.read_csv("data/measurements/turbidity.txt")
conductivity =  pd.read_csv("data/measurements/conductivity.txt")
pH =  pd.read_csv("data/measurements/pH.txt")
algae =  pd.read_csv("data/measurements/algae.txt")

# load data matched directly by nano id
organisms = pd.read_csv("data/measurements/organisms.txt", dtype={"nano_id":int})
positional = pd.read_csv("data/measurements/positional.txt", dtype={"nano_id":int})
sediment = pd.read_csv("data/measurements/sediment.txt", dtype={"nano_id":int})
assessment = pd.read_csv("data/measurements/assessment.txt", dtype={"nano_id":int})
daphnia = pd.read_csv("data/measurements/daphnia.txt", dtype={"nano_id":int})
culex = pd.read_csv("data/measurements/culex.txt", dtype={"nano_id":int})

# construct complete data frame from start of the experiment to today
begin = "2020-11-10"
data = Data.expand_grid({
    "time": pd.date_range(start=begin, end=datetime.today(), freq="D").format(),
    "nano_id": range(1,81)
})

# merge datasets
data = data.merge(organisms,     how="left", left_on=["time", "nano_id"], right_on=["time","nano_id"])
data = data.merge(daphnia,       how="left", left_on=["time", "nano_id"], right_on=["time","nano_id"])
data = data.merge(culex,         how="left", left_on=["time", "nano_id"], right_on=["time","nano_id"])
data = data.merge(positional,    how="left", left_on=["time", "nano_id"], right_on=["time","nano_id"])
data = data.merge(sediment,      how="left", left_on=["time", "nano_id"], right_on=["time","nano_id"])
data = data.merge(assessment,    how="left", left_on=["time", "nano_id"], right_on=["time","nano_id"])
data = data.merge(match,         how="left", left_on=["time", "nano_id"], right_on=["time","nano_id"])
data = data.merge(conductivity,  how="left", left_on=["time","msr_id"], right_on=["time", "msr_id"])
data = data.merge(temperature,   how="left", left_on=["time","msr_id"], right_on=["time", "msr_id"])
data = data.merge(oxygen,        how="left", left_on=["time","msr_id"], right_on=["time", "msr_id"])
data = data.merge(nutrients,     how="left", left_on=["time","msr_id"], right_on=["time", "msr_id"])
data = data.merge(turbidity,     how="left", left_on=["time","msr_id"], right_on=["time", "msr_id"])
data = data.merge(pH,            how="left", left_on=["time","msr_id"], right_on=["time", "msr_id"])
data = data.merge(algae,         how="left", left_on=["time","msr_id"], right_on=["time", "msr_id"])

# finalize data
data = data.rename(columns={"nano_id":"id"}) \
    .drop(columns="msr_id") \
    .set_index(["time","id"]) \
    .dropna(how="all") \
    .to_csv("data/measurements.csv")
