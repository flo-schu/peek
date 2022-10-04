# RUNNING KAARINAS ANALYSIS

__IMPORTANT__: The following steps only work from the main folder of the project
navigate into project folder terminal prompt should look something like this:
<path/to/project/nanocosm>

always start the virtual environment beforehand
<https://docs.python.org/3/tutorial/venv.html>

Example for the dates 26.03.2021 (20210326) and 30.03.2021 (20210330). The
numbers in parentheses can be exchanged or more can be added in the commands in
step 1 and 3

## step 1

`source src/shell/local/1_move_files.sh data/pics`

## step 2

`source src/shell/local/2_read_sessions.sh 20210326 20210330`
process images with normal script to read image files (read_eve.py)

after "read_sessions.sh" __list as many date sessions__ as you want. The program.
will iterate over all of them and read QR codes and copy thumbnails of
errors while reading the qr codes into <data/image_analysis/qr/$DATE> where $DATE
is the same as the input date

This will take a while (~ 20 minutes per date)

## step 3

manually correct QR codes: Go to <data/image_analysis/qr> and add the correct
ids in the column behind the path in <qr_corrections.csv>, when you are done
execute

`source src/shell/local/3_apply_qr_corrections.sh`

a long list of corrections will be printed and mostly nothing is done (these)
are already applied corrections you can ignore them. If unapplied corrections
are worked on the output states so. What happens is that the images are moved
in the correct folders.

## step 3b

choose series where images were taken twice. In <data/pics/${DATE}> replace
${DATE} with the date you want to look for duplicates. Alternatively
you can look at the folders by yourself
`find data/pics/20210413 -mindepth 1 -maxdepth 1 -type d -exec bash -c "echo -ne '{} '; find '{}' -type f -name '*.jpeg' | wc -l" \; | awk '$NF!=3'`

## step 4

`source src/shell/local/4_move_and_rename.sh 20210413 20210416`

This script loops over the folder structure and renames and copies the files
to the directory <data/pics_classic/$DATE>
After this happend Kaarina's analysis can be applied to the images.

## step 5

launch __ImageJ__ and execute from the Plugins "Preparation" and "Detection"
Detection needs to be run twice for Daphnia and Culex
after everything is done. Delete the "#" symbols in fron to the date folders

## step 6

import image data and all measurements. To improve data quality
work on individual measurement scripts
`source src/shell/local/5_import.sh`

## step 7

with evaluate classic, create analyses of the data.
