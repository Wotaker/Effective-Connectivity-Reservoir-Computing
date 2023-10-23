#!/bin/bash -l

METHOD="RCC"
folder_spec=$1
jobs=$2
length=$3
split="70"
skip="5"
runs="20"
surrogates="100"
plots="false"
min_lag="-3"
max_lag="0"

# AOMIC Schaeffer 
subj="${@:4}"
echo "[Debug] Subjects: $subj"
rois="38 39 40 41 42 43 44 45 46 47 48 49 50 90 91 92 93 94 95 96 97 98 99 100"
# rois="-1"
data_dir="Datasets/AOMIC_PIOP_rest_Schaefer100"
results_dir="Results_Specs-"$folder_spec"_AOMIC-Schaefer-100_Split-"$split"_Length-"$length

conda activate $SCRATCH/venvs/rcc-conda-310
echo "[Debug] Env activated"
python -u main_"$METHOD"ausality.py $data_dir -rf $results_dir -j $jobs --split $split --skip $skip --length $length --subjects $subj --rois $rois --num_surrogates $surrogates --runs $runs --min_lag $min_lag --max_lag $max_lag fmri --plots $plots
echo "[Debug] Deactivating env"
conda deactivate
