import os
import numpy as np
from scipy.io import loadmat


def parse_mat_file(mat_file_path: str, destination_dir: str, mat_key: str = "region_mean", subject_first: bool = False):
    """
    Converts the .mat file dataset into the format compatible with the RCC method. File per subject, representing the
    timeseries where each dimension corresponds with each ROI. Timepoints separeted by newline "\\n" and dimensions separated by tab "\\t".

    Parameters
    ----------
    mat_file_path : str
        The path to the .mat file
    destination_dir : str
        The path to the directory that subject files are saved
    mat_key : str, optional
        The key by which the .mat file holds the actual data, by default "region_mean"
    subject_first : bool, optional
        The convention of dims ordering in the .mat file. If subject_first is True, it means that the 1st dimension represents subjects, otherwise it is assumed that the last (3rd) dimension represents subjects, by default False
    """

    data = loadmat(mat_file_path)[mat_key]

    if not subject_first:
        data = np.transpose(data, (2, 0, 1))
    
    for idx, subject in enumerate(data):
        subject_file_name = f"sub-{1+idx:04d}_TS.txt"
        with open(os.path.join(destination_dir, subject_file_name), "w") as subject_file:
            lines = []
            for timestep in subject:
                lines.append("\t".join(list(map(lambda x: f"{x:.06f}", timestep))) + "\n")
            subject_file.writelines(lines)