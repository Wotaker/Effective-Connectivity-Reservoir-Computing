#!/bin/bash

# Parse the first argument as the directory conatining the subject files
directory=$1

# Create an empty file to store the results
result_file=$directory"subjects_list.txt"

# Remove any existing content in the result file
rm -f $result_file

# Loop through each file in the directory
for file in "$directory"*; do
    # Get the filename without extension
    filename=$(basename "$file")
    filename="${filename%.*}"

    # Write the filename to the result file
    echo "$filename" >> $result_file
done

