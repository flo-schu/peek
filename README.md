# nanocosm

Nanocosm experiment with Daphnia Magna and Culex Pipiens

## installation procedure

+ install python
+ create virtual environment named 'env':  python -m venv env
+ activate environment ./env/Scripts/activate (on Linux: source ./env/bin/activate)
+ upgrade pip:   python -m pip install --upgrade pip
+ install requirements: pip install -r requirements.txt

## working on eve cluster

it is recommended to use full paths, because than the scripts can be submitted
from any location, which helps a lot. The whole analysis of all files can probably
be done in less than an hour if there are enough free cores on EVE.

### aliases

aliases are specified in ~/.bashrc
`cdw` cd into work directory of schunckf
`cdh` cd into home directory of schunckf
`pl`  print last file with cat
`sq`  show squeue for user schunckf

useful commands:

+ `sjeff -1d`   successful jobs including ressouce usage
+ `ctrl+r`      search command history
+ `history`     print history
+ `>`           redirect history to file
+ `|`           pipe commands (pass result from one command as input to next)
+ `cat *job-id* exec in logs. get the output and error messages of all array jobs
                concerning this job. Replace job-id with the number
+ `ls -d */ | xargs rm -r` delete all subdirectories but not any files.
+ `find`

### copy files

copy single session to eve
`scp .\20210226\* schunckf@frontend1.eve.ufz.de:/work/schunckf/nanocosm/data/pics/20210226/`

copy all image folders. For this use rsync on cygwin. Everything else did not work
In the future I could try mounting the Y: drive on wsl
I have to try out if the rsync command works now (3) with the last, one an 
extra dictionary was created

1. start cygwin
2. cd into Y: `cd Y:` and `cd Home/schunckf/papers/nanocosm/data`
3. `rsync -avh --progress ./pics schunckf@frontend1.eve.ufz.de:/work/schunckf/nanocosm/data/`

### handling files

count number of files:
`find nanocosm/data/pics/ -mindepth 1 -maxdepth 2 -name "*.RW2" | sort -n | wc -l`

deleting analysis files (tiff, csv, json, npy):
`source /home/schunckf/projects/nanocosm/src/shell/delete_analysis_files.sh /work/schunckf/nanocosm/data/pics/`

move RW2 files out of their directory:
`source /home/schunckf/projects/nanocosm/src/shell/move_files.sh /work/schunckf/nanocosm/data/pics/`

Number of files can be determined with
`tree /work/schunckf/nanocosm/data/pics/20210226/`

### reading images and QR Codes

determine the number of files with `tree /work/schunckf/nanocosm/data/pics/`
this function works also in any other directory because of usage of `find`.
`sbatch -a 1-9352 /home/schunckf/projects/nanocosm/src/shell/read_image_better.sh /work/schunckf/nanocosm/data/pics/`

### detection of organisms

read e.g. first 5 series of a specific session. As an array job. This is fast.
The whole session will be finished in less than a minute
There were memory problems in the past
`sbatch -a 1-5 /home/schunckf/projects/nanocosm/src/shell/detection_series.sh /work/schunckf/nanocosm/data/pics/20210226/ /home/schunckf/projects/nanocosm/settings/masking_20210225.json`

This will perform detection for a whole session (with a loop. Probably not
super efficient, but the algorithm is quite fast. Takes only a few minutes
per session. Can be upscaled for all sessions at once)
`sbatch -a 1-1 /home/schunckf/projects/nanocosm/src/shell/detection_session.sh /work/schunckf/nanocosm/data/pics/ /home/schunckf/projects/nanocosm/settings/masking_20210225.json`

### check QR detection

create an archive of problem qr codes
`source /home/schunckf/projects/nanocosm/src/shell/archive_qrerrors.sh`

get error list
`scp schunckf@frontend1.eve.ufz.de:/work/schunckf/nanocosm/data/qr_errors.txt .\data\image_analysis\QR\qr_errors.txt`

get error image thumbnails
`scp schunckf@frontend1.eve.ufz.de:/work/schunckf/nanocosm/data/qr_errors.tar .\data\image_analysis\QR\qr_errors.tar`

then the image thumbnails have to be checked and the correct id has to be added in a second column next to
the error list (qr_errors.txt). Don't add column names
upload the list again to `/work/schunckf/nanocosm/data/qr/$DATE/qr_corrections.csv` and execute
`source src/shell/apply_qr_corrections.sh > /work/schunckf/nanocosm/data/qr/log.txt`

check if any errors are still present. There should be none after 20201207
`cat /work/schunckf/data/qr/qr_errors_unresolved.txt`

### check if jobs were successful

exchange the job id and output to jobs.txt
`sacct -j 1200452 -o JobID,AveRSS,MaxRSS,CPUTime,TotalCPU,State,Timelimit,Elapsed --units=G > /home/schunckf/projects/data/jobs.txt`
`tree /work/schunckf/nanocosm/data/pics/ > /home/schunckf/projects/data/file_tree.txt`

## priorities

1. [x] __write code that moves all images out of subfolders (for first sessions)__. I pretty sure I can do that easily with a shell script
2. [x] __Control QR codes__. I need to write something which lets me quickly or 
       automatically assign images from 999 to folders
       if the diff to any time is <= 4s, than it can go into the respective folder (this should already fix a lot of the problems)
       for the rest, I can do manual sorting, also I can improve the QR code
       Also it would be nice to code into submit scripts that 999 is always excluded.
       [x] improve QR detection script particularly for 34
3. [ ] classify organisms. Write small tool which accesses the tag file of
       moving edge. Then I can control how well the classification works.
4. [ ] use data tool to collect all data files.
5. [ ] write functions to plot the timeseries (Then I have at least the performance of Daphnia)
6. [ ] continue to build detection database in order to get ML going

Later:

1. [ ] what about zero sized images?
2. [ ] change design of struct path --> relative import to base directory.
       Otherwise its quite shit. should be possible and not too much work.
       Until then, write helper function to strip everything until datefolder
       and preprend current path.
3. [ ] there is a problem with the initial image sessions. Several pictures were
       taken at the same second. Hence here more than one image is present in 
       each the folders sometimes. Because of this the motion analysis scripts will
       fail. The best fix for this would be to improve the folder structure. Because
       it is very good to keep the time folder as the lowest integration unit for
       each image. It would be easiest if time were recorded as nanoseconds. This
       is unlikely. Problematically in array jobs, the image are processed simultaneously
       so that creating folders like 120001_1 if 120001 exist is problematic.
       It would be possible to create a folder like 120001_PNAN001, or simply
       PNAN001 and the name the new file nano.tiff or whatever. Another option
       is to separate files after reading the images was done. For now,
       these folders are ignored.

Done:

1. [x] Important: Write detector for Culex
2. [x] Address memory problems when six images were taken from one nanocosm (need 1.2 GB memory). Not really a problem any more when I can request 20G on cluster :)
3. [x] write cluster script to process images
4. [x] copy all files to work (cygwin and rsync works wonderfully)

copy the following folders with raw data

+ [x] 20210111 delete processed files
+ [x] copy raw files to 20210114
+ [x] copy files in C:/.../pics to Y:/.../pics once my quota was increased
+ [x] execute move file script to files on Y drive, once I made sure to have backed up everythin and then also on harddrive
+ [x] run an analysis and remove files to try if it works
