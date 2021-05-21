import pandas as pd

positional = pd.read_csv("data/raw_measurements/positional_parameters/20210428.csv")
positional.rename(columns={"id":"nano_id", "temp":"midday_temperature", "sediment":"sediment_height"}, 
                  inplace=True)
positional["time"] = "2021-04-28"

positional[["time","nano_id","sediment_height","headspace","radiation","midday_temperature"]] \
    .to_csv("data/measurements/positional.txt", index=False)