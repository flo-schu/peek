#!/usr/bin/env bash
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

# 1. determine new sessions and the number of series for sbatch

# 2. Extract new sessions (not needed any longer. This happens locally)

# 3. Read QR codes (on new sessions unless explicitly stated otherwise) 
#    (if I run the same script twice - just after correcting QR codes, this 
#    should not be triggered again)
#    DETERMINE NUMBER OF FILES (use WC)
sbatch -a 1-9352 "${PROJ_REMOTE}src/shell/read_image_better.sh" "${DATA_REMOTE}pics/"

# 4. Wait until job is done (something with while and sleep)

# 4a. get job id and copy output of sacct, *.err and *.out and download

# 5. archive broken QR codes (omit those which were also marked as 999)
source "${PROJ_REMOTE}src/shell/archive_qrerrors.sh"
# 6. Run QR correction
source "${PROJ_REMOTE}src/shell/apply_qr_corrections.sh" > "${DATA_REMOTE}qr/log.txt"

# 7. run detection and wait until job is done

# 8. archive detection

# SCRIPT C)

# 0. test if jobs are still running.

# 1. download detection

# 2. download QR Problems (here i can comfortably check log and unresolved errors)
rsync -avh --progress "schunckf@frontend1.eve.ufz.de:${DATA_REMOTE}qr" "${DATA_LOCAL}image_analysis"

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