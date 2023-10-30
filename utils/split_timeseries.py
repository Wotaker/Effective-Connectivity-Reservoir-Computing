import os
from tqdm import tqdm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from argparse import ArgumentParser


def explore_files(directory_path: str, min_length: int = 200, plot: bool = True) -> pd.DataFrame:

    def histogram_plot(patological: bool, bins: int = 20):

        plt.hist(lengths_df[lengths_df["Patological"] == patological]['Length'], bins=bins)
        plt.title("Patological subjects" if patological else "Control subjects")
        plt.xlabel("fMRI timesteps")
        plt.savefig(os.path.join(directory_path, f"histogram_{'patological' if patological else 'control'}.png"))
        plt.clf()
    
    def distribution_plot(max_length: int = 1500):

        plt.plot(lengths_df["SubjectName"], lengths_df["Length"], marker='.', linewidth=0.5)
        plt.xticks([])
        plt.ylabel("fMRI timesteps")
        plt.xlabel("Subjects")

        for i in range(2, max_length // min_length + 1):
            plt.axhline(y=i*min_length, color='r', linestyle='-.', alpha=0.5, linewidth=1.0)
            plt.text(150, i*min_length + 10, f"{i}", fontsize=10, color='black')

        plt.savefig(os.path.join(directory_path, f"distribution.png"))
        plt.clf()

    # List all subject files in the directory
    subject_files = os.listdir(directory_path)
    subject_files = [f for f in subject_files if f.endswith('.tsv')]

    # Define helper functions
    timesteps = lambda file: len(pd.read_csv(os.path.join(directory_path, file), sep='\t'))
    subject_name = lambda file: file.split('_')[0]
    subject_type = lambda file: "PAT" in file.split('_')[0]

    # Create dataframe with subject lengths
    lengths_df = list(map(lambda file: (file, subject_name(file), timesteps(file), subject_type(file)), subject_files))
    lengths_df = pd.DataFrame(lengths_df, columns=['FileName', 'SubjectName', 'Length', 'Patological'])
    lengths_df = lengths_df.sort_values(by='Length', ascending=False)

    # Plot results
    if plot:
        histogram_plot(patological=True, bins=20)
        histogram_plot(patological=False, bins=10)
        distribution_plot(max_length=1500)
    
    return lengths_df


def split_file_equally(file: pd.Series, source_dir_path: str, destination_dir_path: str, min_length: int = 200):

    def split_file(file: pd.Series, start: int, end: int, suffix: str):
        # Read the file
        df = pd.read_csv(os.path.join(source_dir_path, file["FileName"]), sep='\t', header=None)

        # Cut the interesting part
        df = df.iloc[start:end+1]

        # Save the file with the new name in the destination directory
        df.to_csv(
            os.path.join(destination_dir_path, file["SubjectName"] + suffix + ".tsv"),
            sep='\t', index=False, header=False
        )
    
    length = file["Length"]
    suffix_id = 65
    if length < 2 * min_length:
        split_file(file, 0, length - 1, chr(suffix_id))
        suffix_id += 1
    else:
        start = 0
        end = min(length, min_length) - 1
        split_file(file, start, end, chr(suffix_id))
        suffix_id += 1
        while end + 2 * min_length < length:
            start += min_length
            end += min_length
            split_file(file, start, end, chr(suffix_id))
            suffix_id += 1
        start += min_length
        end = length - 1
        split_file(file, start, end, chr(suffix_id))
        suffix_id += 1


if __name__ == "__main__":

    # Program arguments
    parser = ArgumentParser()
    parser.add_argument('-s', '--source_dir', type=str, help="Source directory where long files are stored")
    parser.add_argument('-d', '--destination_dir', type=str, help="Destination directory where short files will be stored")
    parser.add_argument('-l', '--min_length', type=int, help="The minimum length of the splitted timeseries")
    parser.add_argument('-p', '--plot', default=False, action='store_true', 
                        help="Should the prior distribution of lengths be plotted?")
    args = parser.parse_args()

    source_dir = args.source_dir
    destination_dir = args.destination_dir
    min_length = args.min_length
    plot = args.plot

    # Explore initial files
    lengths_df = explore_files(source_dir, min_length=min_length, plot=plot)

    # Split files
    # - Create destination directory
    assert not os.path.exists(destination_dir), "Destination directory already exists! Remove it before running this script."
    os.system(f"mkdir {destination_dir}")

    # - Split files
    for index, file in tqdm(lengths_df.iterrows()):
        split_file_equally(file, source_dir, destination_dir, min_length=min_length)
    
    # - Explore files
    explore_files(destination_dir, min_length=min_length, plot=plot)