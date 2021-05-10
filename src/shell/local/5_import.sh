# get data
Rscript "src/read_kaananoij.R"

# get measurements
python "scripts/data_processing/matching.py"
python "scripts/data_processing/temperature.py"
python "scripts/data_processing/conductivity.py"
python "scripts/data_processing/oxygen.py"
python "scripts/data_processing/pH.py"
python "scripts/data_processing/nutrients.py"
python "scripts/data_processing/join_measurements.py"
