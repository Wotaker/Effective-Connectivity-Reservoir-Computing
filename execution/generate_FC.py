from argparse import ArgumentParser

import os
import numpy as np
from nilearn.connectome import ConnectivityMeasure


if __name__ == "__main__":

    # Parse the arguments
    parser = ArgumentParser(description="Generate functional connectivity matrices")
    parser.add_argument("-i", "--input_dir", help="Path to input directory with subject files and subject list")
    parser.add_argument("-o", "--output_dir", help="Output directory to save the functional connectivity matrices")
    parser.add_argument("-e", "--extension", help="Extension of the subject files (default: .tsv)", default=".tsv")
    args = parser.parse_args()

    # Extract the arguments
    input_dir = args.input_dir
    output_dir = args.output_dir
    extension = args.extension
    subjects_list = os.path.join(input_dir, "subjects_list.txt")

    # Load the subjects time series from the list
    subjects_ts = {}
    with open(subjects_list, "r") as f:
        subjects = f.read().splitlines()
        for sub in subjects:
            sub_path = os.path.join(input_dir, sub + extension)
            sub_ts = np.genfromtxt(sub_path, delimiter="\t")
            subjects_ts[sub] = sub_ts
    
    # Compute the functional connectivity matrices
    conn_measure = ConnectivityMeasure(kind="correlation")
    fc_matrices = conn_measure.fit_transform([subjects_ts[sub] for sub in subjects_ts.keys()])

    # Save the functional connectivity matrices
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    for sub, fc_matrix in zip(subjects_ts.keys(), fc_matrices):
        sub_fc_path = os.path.join(output_dir, sub + "_fc_matrix.npy")
        np.save(sub_fc_path, fc_matrix)