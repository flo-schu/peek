#!/usr/bin/env bash
#SBATCH -D /work/%u
#SBATCH -J nanocosm_detection_med
#SBATCH -t 0-01:00:00
#SBATCH -c 4
#SBATCH --mem-per-cpu 20G 
#SBATCH -o /work/%u/logs/%x-%A-%a.out
#SBATCH -e /work/%u/logs/%x-%A-%a.err

echo "processing chunk $SLURM_ARRAY_TASK_ID ..."

PROJECT_DIR="/home/$USER/projects/nanocosm/"
source "$PROJECT_DIR/env/bin/activate"
echo "activated virtual environment"

INPUT_DIR=$1
SETTINGS=$2

SESSION=`find $INPUT_DIR -mindepth 1 -maxdepth 1 -type d | sort -n | head -n $SLURM_ARRAY_TASK_ID | tail -n 1`
echo "processing $SESSION ..."

SERIES=`find $SESSION -mindepth 1 -maxdepth 1 -type d | sort -n | grep -v 999`
for i in $SERIES
    do 
        echo "processing $i ..."
        python "/$PROJECT_DIR/src/detection.py" "$i"
done

echo "finished"