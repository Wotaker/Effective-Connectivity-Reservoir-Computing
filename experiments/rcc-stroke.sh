#!/bin/bash -l

FOLDER_SPEC=$1
SUBJECT=$2
TIMESTAMP=$3

jobs="1"
length="100"
split="90"
skip="10"
runs="20"
surrogates="100"
min_lag="-3"
max_lag="0"
rois="-1"
plots="false"


echo "[Debug] Subject: $SUBJECT"
data_dir="Datasets/stroke"
results_dir="Results_"$FOLDER_SPEC"_"$TIMESTAMP

conda activate $SCRATCH/venvs/rcc-conda-310
echo "[Debug] Env activated"
cd $SCRATCH/Files/GitRepos/Effective-Connectivity-Reservoir-Computing/
python -u main_RCCausality.py $data_dir -rf $results_dir -j $jobs --split $split --skip $skip --length $length --subjects $SUBJECT --rois $rois --num_surrogates $surrogates --runs $runs --min_lag $min_lag --max_lag $max_lag fmri --plots $plots
echo "[Debug] Deactivating env"
conda deactivate
