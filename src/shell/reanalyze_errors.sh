#!/usr/bin/env bash
#SBATCH -D /work/%u
#SBATCH -J read_problems
#SBATCH -t 0-00:01:00
#SBATCH -c 1
#SBATCH --mem-per-cpu 1G
#SBATCH -o /work/%u/logs/%x-%A-%a.out
#SBATCH -e /work/%u/logs/%x-%A-%a.err

echo "processing chunk $SLURM_ARRAY_TASK_ID ..."

PROJECT_DIR="/home/$USER/projects/nanocosm/"
source "$PROJECT_DIR/env/bin/activate"

ERRORFILE=$1

# this line removes '999/123456/' from path and replaces .jpeg with .RW2 
IMG=`$ERRORFILE head -n $SLURM_ARRAY_TASK_ID | tail -n 1 | sed -E "s|999\/([0-9]{6})\/||" | sed 's|.jpeg|.RW2|'`
echo "working on $IMG ..."
# rm -f -v $FILE/*

# python "/$PROJECT_DIR/src/read_eve.py" $IMG -t TRUE