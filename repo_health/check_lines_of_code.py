import os
import subprocess
import pytest
import yaml

from pytest_repo_health import add_key_to_metadata
from repo_health import get_file_content


module_dict_key = "static_analysis"


@pytest.fixture(name="cloc")
def fixture_analyze_lines_of_code(repo_path):
    """Fixture containing the output from running the scc analysis"""
    clock_yaml_str = subprocess.check_output([os.path.join(os.getcwd(), 'scc'), '--format', 'cloc-yaml'])
    return yaml.safe_load(clock_yaml_str)


@add_key_to_metadata((module_dict_key, "lines_of_code"))
def check_lines_of_code(cloc, all_results):
    """
    lines_of_code: number of lines of code in the target directory
    """
    all_results[module_dict_key]["lines_of_code"] = int(cloc['SUM']['code'])


@add_key_to_metadata((module_dict_key, "number_of_files"))
def check_number_of_files(cloc, all_results):
    """
    number_of_files: number of files in the target directory
    """
    all_results[module_dict_key]["number_of_files"] = int(cloc['SUM']['nFiles'])

