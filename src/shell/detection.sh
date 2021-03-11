#!/usr/bin/env bash
#SBATCH -D /work/%u
#SBATCH -J nanocosm_detect
#SBATCH -t 0-01:00:00
#SBATCH --mem-per-cpu 1G 

#SBATCH -o /work/%u/%x-%A-%a.out
#SBATCH -e /work/%u/%x-%A-%a.err

echo "processing chunk $SLURM_ARRAY_TASK_ID ..."

PROJECT_DIR="/home/$USER/projects/nanocosm/"

MY_INPUT_DIR=$1

SERIES=`ls -d $MY_INPUT_DIR*/ | head -n $SLURM_ARRAY_TASK_ID "$MY_INPUT_DIR/dates.txt" | tail -n 1`

echo "processing $SERIES ..."

source "$PROJECT_DIR/env/bin/activate"
python "/$PROJECT_DIR/src/read.py" "$SERIES"