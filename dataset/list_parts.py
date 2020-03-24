
# Dump part names found in all .dat files in given directory, with their corresponding file names, to a JSON file
# Usage: list_parts.py -i <Input_directory_path> -o <Output_file_path>

import argparse
import os
import json
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', type=str, help="Input directory path")
    parser.add_argument('-o', type=str, help="Output file path")
    args = parser.parse_args()
    input_directory = args.i
    output_file = args.o
    part_list = {"parts": []}
    for file_name in sorted(os.listdir(input_directory)):
        if file_name.endswith('.dat'):
            with open(os.path.join(input_directory, file_name), encoding='utf-8') as file:
                # Slicing gets rid of the line type and whitespace
                part_name = file.readline().strip()[2:]
                if '~Moved' not in part_name:
                    part = {"part_name": part_name, "file_name": file_name,
                            "absolute_path": os.path.abspath(os.path.join(input_directory, file_name))}
                    part_list["parts"].append(part)
    with open(output_file, 'w') as out:
        json.dump(part_list, out, indent=4)
