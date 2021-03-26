#!/usr/bin/env bash

LOCAL_PROJ="/c/Users/schunckf/Documents/Florian/papers/nanocosm/"
DATA_STORAGE="/y/Home/schunckf/papers/nanocosm/data/"
REMOTE_PROJ="/Home/schunckf/projects/nanocosm/"
REMOTE_DATA="/work/schunckf/nanocosm/data/"

PROJ_PICS="data/pics/"
PROJ_CORRECTIONS="data/"
# SCRIPT A)

# 0. make directories in work, make sure project directory exists


# 1. Extract new sessions on local drive
`source ${LOCAL_PROJ}src/shell/move_files.sh ${LOCAL_PROJ}${PROJ_PICS}`
echo "extracting pictures in ${LOCAL_PROJ}${PROJ_PICS}"

# 1a. copy pictures to data storage (network drive)

# 2. upload images
rsync -avh --progress "${DATA_STORAGE}pics/" schunckf@frontend1.eve.ufz.de:$REMOTE_DATA

# 3. upload QR corrections
scp ${LOCAL_PROJ}

# 4. start script B) on cluster via ssh

# SCRIPT B)

# 1. determine new sessions and the number of series for sbatch

# 2. Extract new sessions 

# 3. Read QR codes (on new sessions unless explicitly stated otherwise) 
#    (if I run the same script twice - just after correcting QR codes, this 
#    should not be triggered again)
sbatch -a 1-9352 /home/schunckf/projects/nanocosm/src/shell/read_image_better.sh /work/schunckf/nanocosm/data/pics/

# 4. Wait until job is done (something with while and sleep)

# 5. archive broken QR codes (omit those which were also marked as 999)

# 6. Run QR correction

# 7. run detection and wait until job is done

# 8. archive detection

# SCRIPT C)

# 0. test if jobs are still running.

# 1. download detection

# 2. download QR Problems

# 3. extract tarfile

# 4. (?) generating plots

# print now import data can be used


# the problem is that for downloading I need to use the local machine.
# However, if I omit downloading and do it manually whenever I actually need
# the files. I can create a routine which runs on the cluster with the benefit
# that I can upload the files and start the script and then can shut down (on Friday)
# when I come back on monday, I can download the data and take a look.
# For this I'd need three scripts
# - a) upload and start the second script on the remote
# - b) script on remote for QR and DETECTION and archiving 
# - c) script for downloading archives and extraction
#
# the whole script should be transportable by using $USER and so on