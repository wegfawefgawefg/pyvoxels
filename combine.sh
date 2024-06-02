#!/bin/bash

# Check if directory path is provided
if [ -z "$1" ]; then
    echo "Usage: $0 <directory-path>"
    exit 1
fi

# Directory path from the first argument
dir_path="$1"
output_name="$2"

# Output file
output_file="$output_name"

# Empty the output file if it exists
> "$output_file"

# Iterate over each file in the specified directory
for file in "$dir_path"/*; do
    if [[ -f $file ]]; then
        # Add header with newlines
        echo -e "\n////file: $(basename "$file")\n" >> "$output_file"
        # Append the contents of the file
        cat "$file" >> "$output_file"
    fi
done

echo "All files have been combined into $output_file."
