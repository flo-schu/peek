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

### reading files
read a single foto session (takes a few minutes tops). Exchange the image folder specified at the end and increase the number of array jobs if needed (1-N)
`sbatch -a 1-160 /home/schunckf/projects/nanocosm/src/shell/read_image.sh /work/schunckf/nanocosm/data/pics/20210226/`

Number of files can be determined with 
`tree /work/schunckf/nanocosm/data/pics/20210226/`

process for instance 10 sessions (increase with argument 1-N). 
`sbatch -a 1-10 /home/schunckf/projects/nanocosm/src/shell/read_session.sh /work/schunckf/nanocosm/data/pics/`

### detection of organisms
read e.g. first 5 series of a specific session. As an array job. This is fast.
The whole session will be finished in less than a minute
There were memory problems in the past
`sbatch -a 1-5 /home/schunckf/projects/nanocosm/src/shell/detection_series.sh /work/schunckf/nanocosm/data/pics/20210226/ /home/schunckf/projects/nanocosm/settings/masking_20210225.json`

This will perform detection for a whole session (with a loop. Probably not 
super efficient, but the algorithm is quite fast. Takes only a few minutes
per session. Can be upscaled for all sessions at once)
`sbatch -a 1-1 /home/schunckf/projects/nanocosm/src/shell/detection_session.sh /work/schunckf/nanocosm/data/pics/ /home/schunckf/projects/nanocosm/settings/masking_20210225.json`



## priorities

1. [ ] write functions to plot the timeseries (Then I have at least the performance of Daphnia)
2. [ ] Important: Write detector for Culex
3. [ ] write code that moves all images out of subfolders (for first sessions)
4. [ ] Control QR codes
5. [ ] manually label QR codes which could not be read
6. [ ] what about zero sized images?
7. [ ] Address memory problems when six images were taken from one nanocosm (need 1.2 GB memory)
8. [x] write cluster script to process images
9. [ ] change design of struct path --> relative import to base directory. Otherwise its quite shit. should be possible and not too much work. Until then, write helper function
to strip everything until datefolder and preprend current path.
