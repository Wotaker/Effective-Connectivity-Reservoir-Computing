import pandas as pd
import numpy as np
import os

from argparse import ArgumentParser

def parse_combined_subject(subject_dir: str, no_ROIs: int, method_infix: str, only_directed: bool):
    
    subject_name = subject_dir.split('/')[-1].split('_')[0]
    numerical_results = os.path.join(subject_dir, subject_name + '.tsv')
    results_df = pd.read_csv(numerical_results, sep='\t')
    
    lags = np.array(sorted(set(results_df['time-lags'].values)))
    effective_connectivity = np.zeros((lags.shape[0], no_ROIs, no_ROIs))

    # Iterate over all ROI pairs
    for roi_x in range(1, no_ROIs + 1):
        for roi_y in range(1, no_ROIs + 1):

            # Skip diagonal
            if roi_x == roi_y:
                continue

            # Extract causality scores
            filtered_df = results_df[(results_df['ROIx'] == roi_x) & (results_df['ROIy'] == roi_y)]
            score_xy = filtered_df[f'Symetric{method_infix}S'].values
            score_x2y = filtered_df[f'{method_infix}S'].values

            # Assign scores to effective connectivity matrix
            effective_connectivity[:, roi_x - 1, roi_y - 1] = np.nan_to_num(score_x2y + score_xy * (not only_directed))
    
    return lags, effective_connectivity


def get_lags(sample_roi_file_path: str):

    # Read ROI file
    roi_df = pd.read_csv(sample_roi_file_path, sep='\t', index_col=0)

    # Return extracted lags
    return roi_df.index.values


def parse_single_roi(roi_file_path: str, method_infix: str):

    # Read ROI file
    roi_df = pd.read_csv(roi_file_path, sep='\t', index_col=0)

    # Extract ROI variables
    _, x, _, y = roi_df.columns.values[0].split(' ')

    # Extract lags
    lags = roi_df.index.values

    # Extract causality scores
    score_xy = roi_df[f'{method_infix}S {x} <--> {y}'].values
    score_x2y = roi_df[f'{method_infix}S {x} --> {y}'].values
    score_y2x = roi_df[f'{method_infix}S {y} --> {x}'].values

    return lags, score_xy, score_x2y, score_y2x, int(x), int(y)
    

def parse_single_subject(subject_dir: str, no_ROIs: int, method_infix: str):

    # Get all ROI connection files
    numerical_dir = os.path.join(subject_dir, 'Numerical')
    roi_files_paths = []
    for roi_file_name in os.listdir(numerical_dir):
        roi_files_paths.append(os.path.join(numerical_dir, roi_file_name))
    assert roi_files_paths, \
        f'No ROI files found in {numerical_dir}. Try parsing the combined file instead (remove the "--separate" flag).'
    
    # Initialize subject's effective connectivity Matrix with zeros
    lags = get_lags(roi_files_paths[0])
    effective_connectivity = np.zeros((lags.shape[0], no_ROIs, no_ROIs))

    # Parse each ROI pair file
    for roi_file_path in roi_files_paths:
        lags, score_xy, score_x2y, score_y2x, x, y = parse_single_roi(roi_file_path, method_infix)
        effective_connectivity[:, x - 1, y - 1] = np.nan_to_num(score_x2y + score_xy)
        effective_connectivity[:, y - 1, x - 1] = np.nan_to_num(score_y2x + score_xy)
    
    return lags, effective_connectivity
    

def parse_subjects(results_dir: str, no_ROIs: int, method_infix: str, separate: bool, only_directed: bool):

    # Get all subjects directories
    subjects_paths = []
    for subject_dir in os.listdir(results_dir):

        # Skip non-subject directories
        if subject_dir.startswith('sub-'):
            # Skip subjects with no results
            if subject_dir + ".tsv" in os.listdir(os.path.join(results_dir, subject_dir)):
                subjects_paths.append(os.path.join(results_dir, subject_dir))

    # Parse each subject and save effective connectivity matrix to a npy file
    lags_template = None
    for subject_path in subjects_paths:
        subject_name = subject_path.split('/')[-1].split('_')[0]

        if separate:
            lags, effective_connectivity = parse_single_subject(
                subject_path, no_ROIs=no_ROIs, method_infix=method_infix
            )
        else:
            lags, effective_connectivity = parse_combined_subject(
                subject_path, no_ROIs=no_ROIs, method_infix=method_infix, only_directed=only_directed
            )
        
        if lags_template is None:
            lags_template = lags
        else:
            assert np.equal(lags, lags_template).all(), f'lags mismatch for subject {subject_name}'
        
        ec_type = '_onlydirected' if only_directed else ''
        np.save(os.path.join(subject_path, f'{subject_name}{ec_type}.npy'), effective_connectivity)
    
    # Save lag values
    np.save(os.path.join(results_dir, 'lags.npy'), lags_template)


if __name__ == "__main__":

    # Program arguments
    parser = ArgumentParser()
    parser.add_argument('-r', '--results_dir', type=str, help="Output directory where results are stored")
    parser.add_argument('-n', '--no_ROIs', type=int, help="Number of ROIs")
    parser.add_argument('-m', '--method', type=str, default='rcc', choices=['rcc', 'gc'], help="Method used to calculate causality scores")
    parser.add_argument('-s', '--separate', default=False, action='store_true', help="If the results are stored separately")
    parser.add_argument('-d', '--only_directed', default=True, action='store_true', 
                        help="If only directed causality should be considered when calculating score")
    args = parser.parse_args()

    # Parse method infix
    method_infix = 'RCC' if args.method == 'rcc' else 'GC'

    # Parse subjects
    parse_subjects(args.results_dir, args.no_ROIs, method_infix, args.separate, args.only_directed)
