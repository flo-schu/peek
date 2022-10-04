# get data
Rscript "src/read_kaananoij.R"

# get measurements
echo "importing measurement data:"

echo "matching..."
python "scripts/data_processing/matching.py"

echo "temperature..."
python "scripts/data_processing/temperature.py"

echo "conductivity..."
python "scripts/data_processing/conductivity.py"

echo "oxygen..."
python "scripts/data_processing/oxygen.py"

echo "pH..."
python "scripts/data_processing/pH.py"

echo "nutrients..."
python "scripts/data_processing/nutrients.py"

echo "algae..."
python "scripts/data_processing/algae.py"

echo "manual organism count..."
python "scripts/data_processing/organisms.py"

echo "daphnia..."
python "scripts/data_processing/daphnia.py"

echo "culex..."
python "scripts/data_processing/culex.py"

echo "daphnia raw... (takes some minutes)"
python "scripts/data_processing/daphnia_raw.py"

echo "culex raw... (takes some minutes)"
python "scripts/data_processing/culex_raw.py"

echo "additional parameters..."
python "scripts/data_processing/other.py"


echo "------------------------------"

echo "combining data..."
python "scripts/data_processing/join_measurements.py"

echo "final dataset..."
python "scripts/data_processing/final_data.py"

echo "saved output to 'data/measurements.csv'"