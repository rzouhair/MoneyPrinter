#!/bin/bash

# A script that renames all files in a given directory with a sequential number keeping the original file extension

if [ $# -eq 0 ]; then
    echo "Usage: $0 <directory>"
    exit 1
fi

directory="$1"
counter=1

for file in "$directory"/*; do
    if [ -f "$file" ]; then
        extension="${file##*.}"
        new_name=$(printf "%03d.%s" "$counter" "$extension")
        mv "$file" "$directory/$new_name"
        ((counter++))
    fi
done

echo "Files renamed successfully."

# usage: ./rename.sh <directory>