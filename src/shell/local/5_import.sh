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

echo "organisms..."
python "scripts/data_processing/organisms.py"

echo "------------------------------"

echo "combining data..."
python "scripts/data_processing/join_measurements.py"

echo "saved output to 'data/measurements.csv'"