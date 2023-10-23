import pandas as pd
import numpy as np
import os

from argparse import ArgumentParser


def get_lags(sample_roi_file_path: str):

    # Read ROI file
    roi_df = pd.read_csv(sample_roi_file_path, sep='\t', index_col=0)

    # Return extracted lags
    return roi_df.index.values


def parse_single_roi(roi_file_path: str):

    # Read ROI file
    roi_df = pd.read_csv(roi_file_path, sep='\t', index_col=0)

    # Extract ROI variables
    _, x, _, y = roi_df.columns.values[0].split(' ')

    # Extract lags
    lags = roi_df.index.values

    # Extract causality scores
    score_xy = roi_df[f'RCCS {x} <--> {y}'].values
    score_x2y = roi_df[f'RCCS {x} --> {y}'].values
    score_y2x = roi_df[f'RCCS {y} --> {x}'].values

    return lags, score_xy, score_x2y, score_y2x, int(x), int(y)
    

def parse_single_subject(subject_dir: str, no_ROIs: int):

    # Get all ROI connection files
    numerical_dir = os.path.join(subject_dir, 'Numerical')
    roi_files_paths = []
    for roi_file_name in os.listdir(numerical_dir):
        roi_files_paths.append(os.path.join(numerical_dir, roi_file_name))
    
    # Initialize subject's effective connectivity Matrix with zeros
    lags = get_lags(roi_files_paths[0])
    effective_connectivity = np.zeros((lags.shape[0], no_ROIs, no_ROIs))

    # Parse each ROI pair file
    for roi_file_path in roi_files_paths:
        lags, score_xy, score_x2y, score_y2x, x, y = parse_single_roi(roi_file_path)
        effective_connectivity[:, x - 1, y - 1] = np.nan_to_num(score_x2y + score_xy)
        effective_connectivity[:, y - 1, x - 1] = np.nan_to_num(score_y2x + score_xy)
    
    return lags, effective_connectivity
    

def parse_subjects(results_dir: str, no_ROIs: int):

    # Get all subjects directories
    subjects_paths = []
    for subject_dir in os.listdir(results_dir):

        # Skip non-subject directories
        if subject_dir.startswith('sub-'):
            subjects_paths.append(os.path.join(results_dir, subject_dir))
        else:
            continue

    # Parse each subject and save effective connectivity matrix to a npy file
    lags_template = None
    for subject_path in subjects_paths:
        subject_name = subject_path.split('/')[-1].split('_')[0]
        lags, effective_connectivity = parse_single_subject(subject_path, no_ROIs=no_ROIs)

        if lags_template is None:
            lags_template = lags
        else:
            assert np.equal(lags, lags_template).all(), f'lags mismatch for subject {subject_name}'
        
        np.save(os.path.join(subject_path, f'{subject_name}.npy'), effective_connectivity)
    
    # Save lag values
    np.save(os.path.join(results_dir, 'lags.npy'), lags_template)

if __name__ == "__main__":

    # Program arguments
    parser = ArgumentParser()
    parser.add_argument('-r','--results_dir', type=str, help="Output directory where results are stored")
    parser.add_argument('-n','--no_ROIs', type=int, help="Number of ROIs")
    args = parser.parse_args()

    # Parse subjects
    parse_subjects(args.results_dir, args.no_ROIs)
