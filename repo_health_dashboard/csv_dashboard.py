import os
import argparse
import glob
import yaml
import codecs

from utils.utils import squash_and_standardize_dicts, write_squashed_dicts_to_csv

def main():
    parser = argparse.ArgumentParser(description="Create basic dashboard")
    parser.add_argument('--data-dir', 
                        help="location of where data yaml files are located",
                        required=True,
                        dest="data_dir")
    args = parser.parse_args()
    data_dir = os.path.abspath(args.data_dir)
    files = glob.glob(os.path.join(data_dir, "*.yaml"), recursive=False)
    data = {}
    for file_path in files:
        file_name = file_path[file_path.rfind("/")+1:]
        # TODO(jinder): maybe add a try block here
        with codecs.open(file_path, 'r', 'utf-8') as f:
            file_data = f.read()
            parsed_file_data = yaml.safe_load(file_data)
            data[file_name] = parsed_file_data
    output = squash_and_standardize_dicts(data)
    write_squashed_dicts_to_csv(output)



if __name__ == "__main__":
    main()