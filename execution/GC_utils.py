# -*- coding: utf-8 -*-
"""
Original file is located at
    https://colab.research.google.com/drive/1t4Zvi_AfDU2cu6pZYBj_oY6llkskjkn2
"""
import pandas as pd
import numpy as np
import os
from statsmodels.tsa.stattools import grangercausalitytests
from statsmodels.tsa.stattools import adfuller

""" # Stationarity test (not necessary all the time)
# TODO: Incorporate?
for x in range(n_subjects):
  #Compute the stationary test, change the variable to test the other signals
  dftest = adfuller(supplementary, autolag="AIC") #.loc[:,x]
  #Print the p-values showing <0.05 if the test of stationarity is passed
  print(dftest[1]) """

def update_dataframe(
        acc: pd.DataFrame, 
        ROI_x: int,
        ROI_y: int,
        lags: np.ndarray, 
        Score_xy: np.ndarray, 
        Score_x2y: np.ndarray, 
        Score_y2x: np.ndarray,
    ):

    # Create a temporary dataframe to results from x to y
    new_data_xy = pd.DataFrame({
        "time-lags": lags,
        "ROIx": [ROI_x] * len(lags),
        "ROIy": [ROI_y] * len(lags),
        "SymetricGCS": Score_xy,
        "GCS": Score_x2y
    })

    # Create a temporary dataframe to results from y to x
    new_data_yx = pd.DataFrame({
        "time-lags": lags,
        "ROIx": [ROI_y] * len(lags),
        "ROIy": [ROI_x] * len(lags),
        "SymetricGCS": Score_xy,
        "GCS": Score_y2x,
    })

    # Concatenate new data to accumulator and fix data types
    combined = pd.concat([acc, new_data_xy, new_data_yx], axis=0, ignore_index=True)
    combined["time-lags"] = combined["time-lags"].astype(int)

    return combined

def GC_single_subject(subject_file, opts, output_dir, format='svg'):
    """
    TODO: Add description of the function

    Arguments
    -----------
    subject_file: (string) Full path to the file containing the time series. ROI time series are stored as columns.
    TODO: finish arguments

    Outputs
    -----------
    TODO: Add output description.
    """

    length, ROIs, split, skip, runs, N_surrogates, keep_separate = opts.length, opts.rois, opts.split, opts.skip, opts.runs, opts.num_surrogates, opts.keep_separate
    name_subject = subject_file.split("/")[-1].split(".")[0].split("_")[0]
    print(f"Participant ID: {name_subject}")

    # Load time series from subject -- dims: time-points X total-ROIs
    time_series = np.genfromtxt(subject_file)# TODO: Add compatibility, delimiter='\t')
    if np.isnan(time_series[:,0]).all():
        time_series = time_series[:,1:] # First column is dropped due to Nan
    limit = int(time_series.shape[0]*0.01*length)

    # ROIs from input command
    ROIs = list(range(time_series.shape[-1])) if ROIs[0] == -1 else [roi-1 for roi in ROIs]
    no_pairs = {int(0.5 * len(ROIs) * (len(ROIs) - 1))}
    print(f"[Python] No. ROIs: {len(ROIs)} -> No. pairs: {no_pairs}\n")
    print(f"\tROIs: {ROIs}\n")

    # Time series to analyse -- dims: ROIs X 1 X time-points
    TS2analyse = np.expand_dims(
        np.array([time_series[:limit,roi] for roi in ROIs]), axis=1
    )

    # Lags to test; in this scenario, always negative
    min_lag = np.abs(opts.min_lag)
    lags = np.arange(1,min_lag+1)

    # Prepare accumulator dataframe to store results
    accumulator = pd.DataFrame({
        "time-lags": [],
        "ROIx": [],
        "ROIy": [],
        "SymetricGCS": [],
        "GCS": []
    })

    # Destination directories and names of outputs
    output_dir_subject = os.path.join(output_dir,name_subject)
    numerical = os.path.join(output_dir_subject,"Numerical")
    figures = os.path.join(output_dir_subject,"Figures")
    all_rois_csv_path = os.path.join(output_dir_subject, name_subject + '.tsv')

    # Compute GC causality
    run_self_loops = False
    pair_counter = 1
    for i, roi_i in enumerate(ROIs):
        for j in range(i if run_self_loops else i+1, len(ROIs)):
            print(f"[Python] ROI pair {pair_counter} out of {no_pairs}")
            pair_counter += 1

            roi_j = ROIs[j]
            
            data_i2j = np.array([TS2analyse[j,0,:], TS2analyse[i,0,:]]).T
            data_j2i = np.array([TS2analyse[i,0,:], TS2analyse[j,0,:]]).T

            Score_i2j, Score_j2i, Score_ij = np.zeros((len(lags),)), np.zeros((len(lags),)), np.zeros((len(lags),))
            try:
                for t, lag in enumerate(lags):
                    # We only check GC one lag at a time to emulate RCC procedures
                        pvals = grangercausalitytests(data_i2j, maxlag=[lag], verbose=False)[lag][0]
                        Score_i2j[t] = 1 - pvals["ssr_ftest"][1]
                        pvals = grangercausalitytests(data_j2i, maxlag=[lag], verbose=False)[lag][0]
                        Score_j2i[t] = 1 - pvals["ssr_ftest"][1]
            except:
                print(f"Error in {name_subject} with ROIs {roi_i+1}-{roi_j+1}")
                print(data_i2j[:20,:])

            # Destination directories and names of outputs
            output_dir_subject = os.path.join(output_dir,name_subject)
            numerical = os.path.join(output_dir_subject,"Numerical")
            figures = os.path.join(output_dir_subject,"Figures")
            if not os.path.exists(output_dir_subject):
                os.mkdir(output_dir_subject)
            if not os.path.exists(numerical):
                os.mkdir(numerical)
            if not os.path.exists(figures):
                os.mkdir(figures)
            name_subject_GC = name_subject + '_GC_rois-' +str(roi_i+1) + 'vs' + str(roi_j+1)
            name_subject_GC_figure = os.path.join(figures, name_subject_GC+'.' + format)
            name_subject_GC_numerical = os.path.join(numerical ,name_subject_GC+'.tsv')

            # Save numerical results
            i2jlabel, j2ilabel = str(roi_i+1) + ' --> ' + str(roi_j+1), str(roi_j+1) + ' --> ' + str(roi_i+1)

            if keep_separate:
                results = pd.DataFrame({
                    "time-lags": -lags[::-1],
                    "GCS " + i2jlabel: Score_i2j[::-1],
                    "GCS " + j2ilabel: Score_j2i[::-1]
                })
                results.to_csv(name_subject_GC_numerical, index=False, sep='\t', decimal='.')

            accumulator = update_dataframe(
                accumulator,
                roi_i + 1,
                roi_j + 1,
                -lags[::-1],
                Score_ij,
                Score_i2j[::-1],
                Score_j2i[::-1]
            )

            # Is there any ROI-2-ROI figure you can do? Maybe p-values accross lags?

    # Save all results from all ROI-pairs combined in a single file
    accumulator.to_csv(all_rois_csv_path, index=False, sep='\t', decimal='.')
        