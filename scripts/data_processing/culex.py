import pandas as pd
import sys
sys.path.append("src")
import evaluation.calc as calc
from numpy import nanmean

data = pd.read_csv("data/pics_classic/results/c_immo_size.csv") \
    .append(pd.read_csv("data/pics_classic/results/c_mobile_size.csv"))


data = data.query(
        "~ (picture_number == 39 & date == '2021-04-27') |" +
        "~ (picture_number == 48 & date == '2021-05-24') " 
    ) 


data.groupby(["id", "date", "picture"]).count()


counts = data.groupby(["id", "date", "picture"]) \
    .agg(func={"analysis":"size", "value":"mean"}) \
    .reset_index() \
    .rename(columns={"analysis":"culex_count", "value":"culex_size", "date":"time", "id":"nano_id"}) \
    .groupby(["nano_id", "time"]) \
    .agg(func={"culex_count":"max","culex_size":nanmean})



counts.to_csv("data/measurements/culex.txt")

#   select(-c( maximum_n,max_area,total_area,is_max_area,is_maximum, picture_number)) %>% 
#   mutate(bodylength = sqrt(value / 35.5),
#          biomass = 1.5 * 10 ^-8 * (bodylength)^2.84) %>% 
#   select(-value) %>% 
#   # size classes distribution as chosen by kaarina 
#   mutate(sizeclass = case_when(bodylength <= 1.68 ~ "neo",
#                                bodylength <= 2.28 ~ "juvenile",
#                                bodylength >  2.28 ~ "adult")) %>% 
#   ungroup() %>% 