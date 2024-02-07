#!/bin/bash -l

#SBATCH --job-name="ec-networks"
#SBATCH -A plgsano4-cpu
#SBATCH --partition plgrid

#SBATCH --output="/net/ascratch/people/plgwciezobka/Logs/%j-%x-output.out"
#SBATCH --error="/net/ascratch/people/plgwciezobka/Logs/%j-%x-error.err"

#SBATCH --time=00:55:00
#SBATCH -N 1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
##SBATCH --mem-per-cpu=2GB

# Conda environment setting
# GITREPO=$1
# RESULTS_DIR=$2
# NO_ROIS=$3

RESULTS_DIR=$1
METHOD=$2

GITREPO="Effective-Connectivity-Reservoir-Computing"
NO_ROIS="100"

cd $SCRATCH/Files/GitRepos/$GITREPO

conda activate $SCRATCH/venvs/rcc-conda-310
echo "[Debug] Env activated"
python -u ./utils/generate-ec-matrices.py -r "$RESULTS_DIR" -n "$NO_ROIS" -m "$METHOD"
echo "[Debug] Deactivating env"
conda deactivate

# An error may occur if the rois are not ordered like 1, 2, 3, ..., n, where n is the total number of ROIs
