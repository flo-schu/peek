#!/usr/bin/env bash

#############################################################################
# This is a routine bash script to execute the varius steps of image analysis
# on the eve cluster and down and upload files as needed.
# On Windows Cygwin should be used as bash console, because git bash doesn't
# do well on absolute paths
#############################################################################

# TODOS:
# 1. pass moving edge as argument to routine ()

# set environmental variables
PROJ_LOCAL="/cygdrive/c/Users/schunckf/Documents/Florian/papers/nanocosm/"
PROJ_REMOTE="/home/schunckf/projects/nanocosm/"
DATA_LOCAL="${PROJ_LOCAL}data/"
DATA_REMOTE="/work/schunckf/nanocosm/data/"
DATA_STORAGE="/cygdrive/y/Home/schunckf/papers/nanocosm/data/"
DATA_BACKUP="/cygdrive/e/RESEARCH_DATA/nanocosm_2/images/"

# 0. make directories in work, make sure project directory exists


# 1. Extract new sessions on local drive
source "${PROJ_LOCAL}src/shell/move_files.sh" "${DATA_LOCAL}pics/"

# 1a. Copy pics from DATA_LOCAL to DATA_STORAGE (only do in UFZ)
cp "${DATA_LOCAL}/pics" "${DATA_STORAGE}"

# # 1b. Copy pics from DATA_LOCAL to DATA_STORAGE (only do in UFZ)
# cp "${DATA_LOCAL}/pics/*" "${DATA_BACKUP}"

# 2. upload images
rsync -avh --progress "${DATA_STORAGE}pics" "schunckf@frontend1.eve.ufz.de:${DATA_REMOTE}"

# 3. upload QR corrections
rsync -avh --progress "${DATA_LOCAL}image_analysis/qr" "schunckf@frontend1.eve.ufz.de:${DATA_REMOTE}"

# 4. start script B) on cluster via ssh

# SCRIPT B)

DATE=`date +%Y%m%d`

# 1. determine new sessions and the number of series for sbatch

# 2. Extract new sessions (not needed any longer. This happens locally)

# 3. Read QR codes (on new sessions unless explicitly stated otherwise) 
#    (if I run the same script twice - just after correcting QR codes, this 
#    should not be triggered again)
#    DETERMINE NUMBER OF FILES (use WC)

LUPL=16 # process .RW2 files modified last n days (0: today, 1: yesterday, inf: all days)
NJOBS=$(find "${DATA_REMOTE}pics/" -name "*.RW2" -mtime -${LUPL}| 
        sort -n |
        wc -l)
sbatch -a 1- "${PROJ_REMOTE}src/shell/read_image_better.sh" "${DATA_REMOTE}pics/"

# copy 
find "${DATA_REMOTE}pics/" -name "*.RW2" -mtime -${LUPL} > "${DATA_REMOTE}eve_logs/read_images_${DATE}.txt"
LAST_JOB=$(sacct -u schunckf | awk 'END {print $1}' | cut -d _ -f 1)
sacct -j ${LAST_JOB} -o JobID,AveRSS,MaxRSS,CPUTime,TotalCPU,State,Timelimit,Elapsed --units=G > ${DATA_REMOTE}eve_logs/jobs_read.txt

# 4. Wait until job is done (something with while and sleep)

# 5. Run QR correction
source "${PROJ_REMOTE}src/shell/apply_qr_corrections.sh" > "${DATA_REMOTE}qr/log.txt"

# 6. archive broken QR codes (omit those which were also marked as 999)
source "${PROJ_REMOTE}src/shell/archive_qrerrors.sh"

# 7. run detection and wait until job is done ----------------------------------
# getting directories 
PLD=1 # process directories modified last n days (0: today, 1: yesterday, inf: all days)
NJOBS=$(find "${DATA_REMOTE}pics/" -maxdepth 1 -type d -mtime -${PLD} | 
        sort -n | 
        wc -l)

sbatch -a 1-${NJOBS} "${PROJ_REMOTE}src/shell/detection_session.sh" -i="${DATA_REMOTE}pics/" -d=${PLD}


# 8. check for errors ----------------------------------------------------------
LAST_JOB=$(sacct -u schunckf | awk 'END {print $1}' | cut -d _ -f 1)

# detection output and errors
cat /work/schunckf/logs/moving_edge-${LAST_JOB}-*.out > "${DATA_REMOTE}eve_logs/moving_edge.out"
cat /work/schunckf/logs/moving_edge-${LAST_JOB}-*.err > "${DATA_REMOTE}eve_logs/moving_edge.err"

# check cluster info
sacct -j ${LAST_JOB} -o JobID,AveRSS,MaxRSS,CPUTime,TotalCPU,State,Timelimit,Elapsed --units=G > ${DATA_REMOTE}eve_logs/jobs_moving_edge.txt

# print file tree
tree "${DATA_REMOTE}pics/" > "${DATA_REMOTE}eve_logs/file_tree.txt"

# 9. archive detection ---------------------------------------------------------
source "${PROJ_REMOTE}src/shell/archive_analysis.sh" moving_edge

# SCRIPT C)

# 0. test if jobs are still running.

# 0. download logs
rsync -avh --progress "schunckf@frontend1.eve.ufz.de:${DATA_REMOTE}eve_logs" "${DATA_LOCAL}image_analysis"

# 1. download detection (slim only csv files)
scp "schunckf@frontend1.eve.ufz.de:${DATA_REMOTE}analyses/moving_edge-${DATE}-slim.tar" "${DATA_LOCAL}annotations/"
tar -C "${DATA_LOCAL}annotations/" -xvf "${DATA_LOCAL}annotations/moving_edge-${DATE}-slim.tar"
rsync -a ${DATA_LOCAL}annotations${DATA_REMOTE}pics/ ${DATA_LOCAL}annotations/
rm -rf ${DATA_LOCAL}annotations/work
rm "${DATA_LOCAL}annotations/moving_edge-${DATE}-slim.tar"

# 2. download QR Problems (here i can comfortably check log and unresolved errors)
rsync -avh --progress "schunckf@frontend1.eve.ufz.de:${DATA_REMOTE}qr" "${DATA_LOCAL}image_analysis"

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