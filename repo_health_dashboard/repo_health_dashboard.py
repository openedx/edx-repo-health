"""
repo-health-dashboard CLI
"""

import os
import argparse
import glob
import codecs
import datetime

import yaml

from .utils import utils


def get_repo_health_data_files(path, repos_to_skip):
    """
    returns a list for yaml files to aggregate health dashboard data from while skipping ones with failed pytest repo
    health checks
    """
    data_files_to_skip = ["{0}_repo_health.yaml".format(repo_name) for repo_name in repos_to_skip]
    data_files = glob.glob(os.path.join(path, "*.yaml"), recursive=False)

    def should_skip_file(data_file):
        file_name = os.path.splitext(os.path.basename(data_file))[0]
        return file_name in data_files_to_skip
    return [data_file for data_file in data_files if should_skip_file(data_file)]


def main():
    """
    Create basic dashboard
    """
    parser = argparse.ArgumentParser(description="Create basic dashboard")
    parser.add_argument(
        "--data-dir",
        help="location of where data yaml files are located",
        required=True,
        dest="data_dir",
    )
    parser.add_argument(
        "--output-csv",
        help="path to csv output",
        dest="output_csv",
        default="dashboard",
    )
    parser.add_argument(
        "--configuration",
        help="path to yaml file with configurations for key orders and aliases",
        default=None,
    )
    parser.add_argument(
        "--data-life-time",
        help="days: how many days before individual data yaml files are outdated",
        default=1,
    )
    parser.add_argument(
        "--skip",
        help="Comma separated string of repository names to skip from repo health data aggregation",
        default="",
    )
    args = parser.parse_args()
    # collect configurations if they were input
    configurations = {
        "main": {"check_order": [], "repo_name_order": [], "key_aliases": {}}
    }

    if args.configuration:
        with codecs.open(args.configuration, "r", "utf-8") as f:
            file_data = f.read()
            parsed_file_data = yaml.safe_load(file_data)
            sheets = parsed_file_data.keys()
            for sheet in sheets:
                configurations[sheet] = utils.get_sheets(parsed_file_data, sheet)

    data_dir = os.path.abspath(args.data_dir)
    repos_to_skip = args.skip.split(",")
    files = get_repo_health_data_files(data_dir, repos_to_skip)
    data = {}
    for file_path in files:
        file_name = file_path[file_path.rfind("/") + 1 :]
        repo_name = file_name.replace("_repo_health.yaml", "")
        # TODO(jinder): maybe add a try block here
        with codecs.open(file_path, "r", "utf-8") as f:
            file_data = f.read()
            parsed_file_data = yaml.safe_load(file_data)
            date_of_collection = parsed_file_data["TIMESTAMP"]
            today_date = datetime.datetime.now().date()
            days_since_collection = abs((today_date - date_of_collection).days)
            if days_since_collection > args.data_life_time:
                continue
            data[repo_name] = parsed_file_data
    output = utils.squash_and_standardize_metadata_by_repo(data)
    for key, configuration in configurations.items():
        utils.write_squashed_metadata_to_csv(
            output, args.output_csv + "_" + key, configuration
        )


if __name__ == "__main__":
    main()
