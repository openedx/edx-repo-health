import os
import argparse
import glob
import yaml
import codecs
import pdb

from utils.utils import squash_and_standardize_metadata_by_repo, write_squashed_metadata_to_csv

def main():
    parser = argparse.ArgumentParser(description="Create basic dashboard")
    parser.add_argument('--data-dir', 
                        help="location of where data yaml files are located",
                        required=True,
                        dest="data_dir")

    parser.add_argument('--output_csv', 
                        help="path to csv output",
                        dest="output_csv",
                        default="dashboard.csv")
    parser.add_argument('--configuration', 
                        help="path to yaml file with configurations for key orders and aliases",
                        default=None)
    args = parser.parse_args()

    # collect configurations if they were input
    configuration = {"check_order":[], 'repo_name_order':[], 'key_aliases':{}}
    if args.configuration:
        with codecs.open(args.configuration, 'r', 'utf-8') as f:
            file_data = f.read()
            parsed_file_data = yaml.safe_load(file_data)
            configuration["check_order"] = parsed_file_data.get("check_order",[])
            configuration['repo_name_order'] = parsed_file_data.get('repo_name_order',[])
            configuration['key_aliases'] = parsed_file_data.get('key_aliases',{})

    data_dir = os.path.abspath(args.data_dir)
    files = glob.glob(os.path.join(data_dir, "*.yaml"), recursive=False)
    data = {}
    for file_path in files:
        file_name = file_path[file_path.rfind("/")+1:]
        repo_name = file_name.replace("_repo_health.yaml", "")
        # TODO(jinder): maybe add a try block here
        with codecs.open(file_path, 'r', 'utf-8') as f:
            file_data = f.read()
            parsed_file_data = yaml.safe_load(file_data)
            data[repo_name] = parsed_file_data
    output = squash_and_standardize_metadata_by_repo(data)
    write_squashed_metadata_to_csv(output, args.output_csv, configuration)



if __name__ == "__main__":
    main()
