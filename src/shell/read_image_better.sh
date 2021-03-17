#!/usr/bin/env bash
#SBATCH -D /work/%u
#SBATCH -J nanocosm_read
#SBATCH -t 0-00:01:00
#SBATCH -c 1
#SBATCH --mem-per-cpu 10G 
#SBATCH -o /work/%u/logs/%x-%A-%a.out
#SBATCH -e /work/%u/logs/%x-%A-%a.err

echo "processing chunk $SLURM_ARRAY_TASK_ID ..."

PROJECT_DIR="/home/$USER/projects/nanocosm/"

source "$PROJECT_DIR/env/bin/activate"
INPUT_DIR=$1

IMG=`find $INPUT_DIR -name "*.RW2" | sort -n | head -n $SLURM_ARRAY_TASK_ID | tail -n 1`

echo "working on $IMG ..."
python "/$PROJECT_DIR/src/read_eve.py" $IMG