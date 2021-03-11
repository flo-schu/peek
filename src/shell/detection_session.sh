#!/usr/bin/env bash
#SBATCH -D /work/%u
#SBATCH -J nanocosm_detection_med
#SBATCH -t 0-01:00:00
#SBATCH --mem-per-cpu 12G 
#SBATCH -o /work/%u/logs/%x-%A-%a.out
#SBATCH -e /work/%u/logs/%x-%A-%a.err

echo "processing chunk $SLURM_ARRAY_TASK_ID ..."

PROJECT_DIR="/home/$USER/projects/nanocosm/"
source "$PROJECT_DIR/env/bin/activate"
echo "activated virtual environment"

INPUT_DIR=$1
SESSION=`ls -d $INPUT_DIR*/ | head -n $SLURM_ARRAY_TASK_ID | tail -n 1`
echo "processing $SESSION ..."

SERIES=`ls -d $SESSION*/`
for i in $SERIES
    do 
        echo "processing $i ..."
        python "/$PROJECT_DIR/src/detection.py" "$i" "$SETTINGS"
done

echo "finished"