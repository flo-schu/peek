#!/usr/bin/env bash
#SBATCH -D /work/%u
#SBATCH -J nanocosm_detection_series_med
#SBATCH -t 0-00:05:00
#SBATCH --mem-per-cpu 12G 
#SBATCH -o /work/%u/logs/%x-%A-%a.out
#SBATCH -e /work/%u/logs/%x-%A-%a.err

echo "processing chunk $SLURM_ARRAY_TASK_ID ..."

INPUT_DIR=$1
SETTINGS=$2
SERIES=`ls -d $INPUT_DIR*/ | head -n $SLURM_ARRAY_TASK_ID | tail -n 1`

echo "processing $SERIES ..."

PROJECT_DIR="/home/$USER/projects/nanocosm/"
source "$PROJECT_DIR/env/bin/activate"
python "/$PROJECT_DIR/src/detection.py" "$SERIES" "$SETTINGS"