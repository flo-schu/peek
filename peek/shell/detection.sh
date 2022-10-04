#!/usr/bin/env bash
#SBATCH -D /work/%u
#SBATCH -J nanocosm_detection_series_med
#SBATCH -t 0-00:30:00
#SBATCH --mem-per-cpu 20G 
#SBATCH -o /work/%u/logs/%x-%A-%a.out
#SBATCH -e /work/%u/logs/%x-%A-%a.err

echo "processing chunk $SLURM_ARRAY_TASK_ID ..."

DEPTH=$1
INPUT_DIR=$2
# SETTINGS=$3
SERIES=`find $INPUT_DIR -mindepth $DEPTH -maxdepth $DEPTH -type d | sort -n | grep -v 999 | head -n $SLURM_ARRAY_TASK_ID | tail -n 1`

echo "processing $SERIES ..."

PROJECT_DIR="/home/$USER/projects/nanocosm/"
source "$PROJECT_DIR/env/bin/activate"
python "/$PROJECT_DIR/src/detection.py" "$SERIES"