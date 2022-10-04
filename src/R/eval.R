library(drc)
obs <- read.csv("data/pre_experiment/20210217/pesticide_trials_observations.csv")
trt <- read.csv("data/pre_experiment/20210217/pesticide_trials_treatments.csv")

source("src/R/drm.R")

use_cols <- ! colnames(obs) %in% c("treatment", "comment_20210219.1")
data <- merge(trt, obs[, use_cols], by = "id")

colnames(data)

data[, "survival_20210219"] <- data[, "survival_20210219"] / data[, "survival_20210217"] 
data[, "survival_20210223"] <- data[, "survival_20210223"] / data[, "survival_20210217"] 

drm_DE <- make_drm(
    data = data, 
    dose = c("concentration", "Esfenvalerate concentration µg L-1"),
    response = c("survival_20210223", "survival Daphnia 6 days"),
    data_sub = list(pesticide = "Efenvalerate", species = "Daphnia"),
    max_response = 0, min_response = 1,
    # save_plot_to = "plots/20210217_pre_experiment/Esfen_Daphnia"
)



drm_CE <- make_drm(
    data = data, 
    dose = c("concentration", "concentration µg L-1"),
    response = c("survival_20210223", "survival Culex 6 days"),
    data_sub = list(pesticide = "Esfenvalerate", species = "Culex"),
    max_response = 0, min_response = 1,
    dose_predict = seq(0, 1, by = .001)
    # save_plot_to = "plots/20210217_pre_experiment/Esfen_Culex"
)

plot(drm_CE$prediction[,3] ~ drm_CE$prediction[,1], log="x")

drc::ED(drm_DE$drm_normalized, c(1,10, 50,90, 99))
drc::ED(drm_CE$drm_normalized, c(1,10, 50,90, 99))


# DMSO concentration DRM ---
data[, "DMSO_concentration"] <- data[, "vol.DMSO.µL"] / data[, "Vol.ml"] 

make_drm(
    data = data, 
    dose = c("DMSO_concentration", "DMSO concentration vol %"),
    response = c("survival_20210223", "survival Daphnia 6 days"),
    data_sub = list(pesticide = "DMSO", species = "Daphnia"),
    max_response = 0, min_response = 1,
    # save_plot_to = "plots/20210217_pre_experiment/Esfen_Daphnia"
)



## pre experiment 2

obs <- read.csv("data/pre_experiment/20210224/pesticide_trials_observations.csv")
trt <- read.csv("data/pre_experiment/20210224/pesticide_trials_treatments.csv")

source("src/R/drm.R")

use_cols <- ! colnames(obs) %in% c("treatment", "size_class")
data <- merge(trt, obs[, use_cols], by = "id")

colnames(data)

data[, "survival_20210226"] <- data[, "survival_20210226"] / data[, "n_organisms"] 
data[, "survival_20210302"] <- data[, "survival_20210302"] / data[, "n_organisms"] 

drm_DE <- make_drm(
    data = data, 
    dose = c("concentration", "Esfenvalerate concentration µg L-1"),
    response = c("survival_20210302", "survival Daphnia after 6 days"),
    data_sub = list(size_class = "large", species="Daphnia"),
    max_response = 0, min_response = 1,
    # save_plot_to = "plots/20210217_pre_experiment/Esfen_Daphnia"
)
