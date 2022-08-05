#!/usr/bin/env bash
#SBATCH --job-name=detection
#SBATCH --time=0-00:05:00
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=12G 
#SBATCH --output=/work/%u/nanocosm/logs/%x-%A-%a.out
#SBATCH --error=/work/%u/nanocosm/logs/%x-%A-%a.err
#SBATCH --mail-type=begin                              # send mail when job begins
#SBATCH --mail-type=end                                # send mail when job ends
#SBATCH --mail-type=fail                               # send mail if job fails
#SBATCH --mail-user=florian.schunck@ufz.de             # email of user


echo "processing chunk $SLURM_ARRAY_TASK_ID ..."

INPUT_DIR=$1
CONFIG=$2
# SETTINGS=$3
SERIES=`find $INPUT_DIR -mindepth 2 -maxdepth 2 -type d | 
    sort -n | 
    grep -v 999 | 
    head -n $SLURM_ARRAY_TASK_ID | 
    tail -n 1`

echo "processing $SERIES ..."

module purge
module load foss/2019b

PROJECT_DIR="/home/$USER/projects/nanocosm/"
source "$PROJECT_DIR/env/bin/activate"
python "$PROJECT_DIR/src/detection.py" \
    "$SERIES" \
    --config=CONFIG