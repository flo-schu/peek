import pandas as pd
import numpy as np

# import positional parameters
positional = pd.read_csv("data/raw_measurements/other/positional.csv") 
positional.rename(columns={"temp":"midday_temperature", "sediment":"sediment_height"}, inplace=True)
positional["time"] = pd.to_datetime(positional.time, format="%Y%m%d")
positional["position"] = np.repeat([1,2,3,4] , 20)

temperature = pd.read_csv("data/raw_measurements/other/temperature_20210526.csv")
temperature.rename(columns={"temp_morning":"morning_temperature"}, inplace=True)
temperature["time"] = pd.to_datetime(temperature.time, format="%Y%m%d")

positional = positional.append(temperature)


# import sediment assessment
sediment = pd.read_csv("data/raw_measurements/other/sediment.csv")
sediment["time"] = pd.to_datetime(sediment.time, format="%Y%m%d")

# import status assessment
assessment = pd.read_csv("data/raw_measurements/other/subjective_status_assessment.csv")
assessment["time"] = pd.to_datetime(assessment.time, format="%Y%m%d")


# save files
sediment.to_csv("data/measurements/sediment.txt", index=False)
assessment.to_csv("data/measurements/assessment.txt", index=False)
positional.to_csv("data/measurements/positional.txt", index=False)