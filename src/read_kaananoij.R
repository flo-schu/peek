source("../nanomodel/src/R/01_data_import.R")

# import Daphnia Area
d <- import_nano(
    path = "data/pics_classic",
    fname = "Erg_gross.txt",
    n = 80,
    species = "Daphnia",
    out = "data/pics_classic/results/d_size.csv")

# import immobile Culex
ci <- import_nano(
    path = "data/pics_classic",
    fname = "#AbundImmo.txt",
    n = 80,
    species = "Culex",
    analysis = "edge",
    out = "data/pics_classic/results/c_immo_size.csv")

# import mobile Culex
cm <- import_nano(
    path = "data/pics_classic",
    fname = "#AbundMobil.txt",
    n = 80,
    species = "Culex",
    out = "data/pics_classic/results/c_mobile_size.csv")


