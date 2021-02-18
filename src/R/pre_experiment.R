# pre experiment preparation 17.02.2021
library(tidyverse)

db <- expand.grid(
    # replicate_id = c(1,2,3,4),
    species = c("Daphnia", "Culex"),
    solution = c(0, 1, 2, 3, 4, 5),
    pesticide = c("DMSO", "Esfenvalerate", "Chlorantraniliprole", "Fipronil")
)


data <- db  %>% mutate(
    id = seq(nrow(db)),
    p = substr(pesticide, 1, 1),
    d = "_",
    c = solution,
    s = substr(species, 1, 1)
) %>% 
    unite(s,d,p,c, col="treatment", sep="") %>% 
    select(id, treatment, pesticide, species, solution)


write.csv(data, "data/pre_experiment/pesticide_trials.csv")
