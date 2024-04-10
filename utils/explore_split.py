import os
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

if __name__ == "__main__":

    # Program arguments
    parser = ArgumentParser()
    parser.add_argument('-s', '--source_dir', type=str, required=True, help="Source directory where timeseries files are stored")
    parser.add_argument('-l', '--min_length', type=int, default=200, help="The minimum length of the splitted timeseries")
    parser.add_argument('-p', '--plot', default=True, action='store_false', 
                        help="Should the prior distribution of lengths be plotted?")
    args = parser.parse_args()

    source_dir = args.source_dir
    min_length = args.min_length
    plot = args.plot

    # Explore initial files
    explore_files(source_dir, min_length=min_length, plot=plot)