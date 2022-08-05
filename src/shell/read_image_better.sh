#!/usr/bin/env bash
#SBATCH --job-name=readqr
#SBATCH --time=0-00:01:00
#SBATCH --nodes=1
#SBATCH --mem-per-cpu=10G 
#SBATCH --output=/work/%u/nanocosm/logs/%x-%A-%a.out
#SBATCH --error=/work/%u/nanocosm/logs/%x-%A-%a.err
#SBATCH --mail-type=begin                              # send mail when job begins
#SBATCH --mail-type=end                                # send mail when job ends
#SBATCH --mail-type=fail                               # send mail if job fails
#SBATCH --mail-user=florian.schunck@ufz.de             # email of user

echo "processing chunk $SLURM_ARRAY_TASK_ID ..."

PROJECT_DIR="/home/$USER/projects/nanocosm/"

source "$PROJECT_DIR/env/bin/activate"
INPUT_DIR=$1

IMG=`find $INPUT_DIR -name "*.RW2" | sort -n | head -n $SLURM_ARRAY_TASK_ID | tail -n 1`

echo "working on $IMG ..."
python "/$PROJECT_DIR/src/read_eve.py" $IMG -t TRUE