# RUNNING KAARINAS ANALYSIS

__IMPORTANT__: The following steps only work from the main folder of the project
navigate into project folder terminal prompt should look something like this:
<path/to/project/nanocosm>

Example for the dates 26.03.2021 (20210326) and 30.03.2021 (20210330). The
numbers in parentheses can be exchanged or more can be added in the commands in
step 1 and 3

## step 1

`source src/shell/1_read_sessions.sh 20210326 20210330`
process images with normal script to read image files (read_eve.py)

after "read_sessions.sh" __list as many date sessions__ as you want. The program
will iterate over all of them and read QR codes and copy thumbnails of
errors while reading the qr codes into <data/image_analysis/qr/$DATE> where $DATE
is the same as the input date

This will take a while (~ 20 minutes per date)

## step 2

manually correct QR codes: Go to <data/image_analysis/qr> and add the correct
ids in the column behind the path in <qr_corrections.csv>, when you are done
execute

`source src/shell/2_apply_qr_corrections.sh`

a long list of corrections will be printed and mostly nothing is done (these)
are already applied corrections you can ignore them. If unapplied corrections
are worked on the output states so. What happens is that the images are moved
in the correct folders.

## step 3

`source src/shell/3_move_and_rename.sh 20210326 20210330`

This script loops over the folder structure and renames and copies the files
to the directory <data/pics_classic/$DATE>
After this happend Kaarina's analysis can be applied to the images.
