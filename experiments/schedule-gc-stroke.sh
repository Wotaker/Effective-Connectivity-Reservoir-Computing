#!/bin/bash -l

TIMESTAMP=$(date +%y%m%d_%H%M%S)
FOLDER_SPEC="gc-stroke"
GITREPO="Effective-Connectivity-Reservoir-Computing"
DATA_DIR=$SCRATCH/Files/GitRepos/$GITREPO/Datasets/stroke-split/
RESULTS_DIR=$SCRATCH/Files/GitRepos/$GITREPO/Results-$FOLDER_SPEC/

# Create directory structure to store logs
mkdir -p $SCRATCH/Logs/gc-stroke/
mkdir -p $SCRATCH/Logs/gc-stroke/$TIMESTAMP/

# - and results
mkdir -p $RESULTS_DIR
RESULTS_DIR=$RESULTS_DIR/$TIMESTAMP/
mkdir -p $RESULTS_DIR

# cd to directory containing stroke fMRI files
cd $DATA_DIR

# The file with the list of subjects to analize
# - subjects names should not have file extension!
# - so the line "sub-PAT175A" is valid but "sub-PAT175A.tsv" is not!
# - generate this file with `/Effective-Connectivity-Reservoir-Computing/utils/list-subjects.sh $DATA_DIR`
subjects_list="subjects_list.txt"

# Read the subjects names from the subjects list
while read subject; do
  # Process the subject
  # sbatch $SCRATCH/Jobs/launch-gc-stroke.sh $subject $FOLDER_SPEC $DATA_DIR $RESULTS_DIR
  LOG_OUTPUT_DIR=$SCRATCH/Logs/$FOLDER_SPEC/$TIMESTAMP/$subject-output.out
  LOG_ERROR_DIR=$SCRATCH/Logs/$FOLDER_SPEC/$TIMESTAMP/$subject-error.err
  sbatch --job-name="$FOLDER_SPEC" --account="plgsano4-cpu" --partition="plgrid" --output="$LOG_OUTPUT_DIR" --error="$LOG_ERROR_DIR" --time="72:00:00" --nodes="1" --ntasks-per-node="1" --cpus-per-task="1" --mem-per-cpu="1GB" $SCRATCH/Files/GitRepos/$GITREPO/experiments/gc-stroke.sh $subject $DATA_DIR $RESULTS_DIR
done < "$subjects_list"
