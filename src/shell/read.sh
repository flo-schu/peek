#!/usr/bin/env bash
#SBATCH -D /work/%u
#SBATCH -J nanocosm_read
#SBATCH -t 0-00:05:00
#SBATCH --mem-per-cpu 1G 

#SBATCH -o /work/%u/%x-%A-%a.out
#SBATCH -e /work/%u/%x-%A-%a.err

echo "processing chunk $SLURM_ARRAY_TASK_ID ..."

PROJECT_DIR="/home/$USER/projects/nanocosm/"

source "$PROJECT_DIR/env/bin/activate"
MY_INPUT_DIR=$1

python "/$PROJECT_DIR/src/read.py" "$MY_INPUT_DIR" -f $SLURM_ARRAY_TASK_ID