# pre experiment preparation 17.02.2021
library(tidyverse)

db <- expand.grid(
    # replicate_id = c(1,2,3,4),
    species = c("Daphnia", "Culex"),
    solution = c(0, 1, 2, 3, 4, 5),
    pesticide = c("DMSO", "Esfenvalerate", "Chlorantraniliprole", "Fipronil")
)


data <- db %>%
    mutate(
        id = seq(nrow(db)),
        p = substr(pesticide, 1, 1),
        d = "_",
        c = solution,
        s = substr(species, 1, 1)
    ) %>%
    unite(s, d, p, c, col = "treatment", sep = "") %>%
    select(id, treatment, pesticide, species, solution)


write.csv(data, "data/pre_experiment/pesticide_trials.csv")



# pre experiment preparation 24.02.2021

db <- expand.grid(
    # replicate_id = c(1,2,3,4),
    size_class = c("small", "medium", "large"),
    species = c("Daphnia", "Culex"),
    solution = c("E0", "E1", "E2", "E3", "E4", "E5"),
    pesticide = c("Esfenvalerate"),
    n_organisms = 3,
    amount_food = 0,
    medium = "ADAM",
    start = "24.02.2021 16:00",
    stringsAsFactors = FALSE
)

data <- db %>%
    mutate(
        id = seq(nrow(db)),
        d = "_",
        c = solution,
        s = substr(species, 1, 1)
    ) %>%
    unite(s, d, c, col = "treatment", sep = "") %>%
    select(id, treatment, everything())

write.csv(data, "data/pre_experiment/20210224/pesticide_treatments_labbook.csv")
data

solutions <- data.frame(
    solution = c("E0", "E1", "E2", "E3", "E4", "E5"),
    vol_mL = 80,
    vol_DMSO_µL = c(0, 8, 80, 16, 80, 16),
    concentration = c(0, 0.0016, 0.008, 0.04, 0.2, 1),
    stringsAsFactors = FALSE
)

data <- merge(data, solutions, by = "solution")
write.csv(data, "data/pre_experiment/20210224/pesticide_trials_treatments.csv")




