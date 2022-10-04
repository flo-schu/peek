#!/usr/bin/env bash
#SBATCH -D /work/%u
#SBATCH -J moving_edge
#SBATCH -t 0-01:00:00
#SBATCH -c 4
#SBATCH --mem-per-cpu 20G 
#SBATCH -o /work/%u/logs/%x-%A-%a.out
#SBATCH -e /work/%u/logs/%x-%A-%a.err

for i in "$@"
do
case $i in
    -i=*|--input=*)
    INPUT_DIR="${i#*=}"
    shift # past argument=value
    ;;
    -c=*|--config=*)
    CONFIG="${i#*=}"
    shift # past argument=value
    ;;
    -d=*|--process-last-days=*)
    DAYS="${i#*=}"
    shift # past argument=value
    ;;
esac
done

DAYS=${DAYS:-"inf"}

PROJECT_DIR="/home/$USER/projects/nanocosm/"
source "$PROJECT_DIR/env/bin/activate"

echo "activated virtual environment"
echo "processing files from ${INPUT_DIR}, modified ${DAYS} days before today"
echo "processing chunk $SLURM_ARRAY_TASK_ID ..."

SESSION=$(find $INPUT_DIR -mindepth 1 -maxdepth 1 -type d -mtime -${DAYS} | 
          sort -n | 
          head -n $SLURM_ARRAY_TASK_ID | 
          tail -n 1)

echo "processing Session: $SESSION ..."

SERIES=$(find $SESSION -mindepth 1 -maxdepth 1 -type d | 
         sort -n | 
         grep -v 999 |
         grep -v 34)

for s in $SERIES
    do 
        echo "processing $s ..."
        python "/$PROJECT_DIR/src/detection.py" "$s"
done

echo "finished"

unset INPUT_DIR
unset CONFIG
unset DAYS
unset PROJECT_DIR
unset SESSION
unset SERIES