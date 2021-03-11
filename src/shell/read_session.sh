#!/usr/bin/env bash
#SBATCH -D /work/%u
#SBATCH -J nanocosm_read
#SBATCH -t 0-01:00:00
#SBATCH --mem-per-cpu 1G 
#SBATCH -o /work/%u/%x-%A-%a.out
#SBATCH -e /work/%u/%x-%A-%a.err

echo "processing chunk $SLURM_ARRAY_TASK_ID ..."

INPUT_DIR=$1
SESSION=`ls -d $INPUT_DIR*/ | head -n $SLURM_ARRAY_TASK_ID | tail -n 1`

echo "processing $SESSION ..."

PROJECT_DIR="/home/$USER/projects/nanocosm/"
source "$PROJECT_DIR/env/bin/activate"
python "/$PROJECT_DIR/src/read.py" "$SESSION"