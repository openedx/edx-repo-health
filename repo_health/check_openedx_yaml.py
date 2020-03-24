"""
Checks to see if openedx.yaml follows minimum standards
And gathers info
"""
import pytest
import yaml
import os

from repo_health import get_file_content
# Decision: require openedx.yaml to be parsable

module_dict_key = "openedx_yaml"

@pytest.fixture
def openedx_yaml(repo_path):
    """Fixture containing the text content of openedx.yaml"""
    full_path = os.path.join(repo_path, 'openedx.yaml')
    return get_file_content(full_path)

@pytest.fixture
def parsed_data(openedx_yaml):
    """
    Parses openedx.yaml returns resulting dict.
    """
    try:
        data = yaml.safe_load(openedx_yaml)
        if data is None:
            return {}
        return data
    except yaml.YAMLError:
        return {}

def check_yaml_parsable(openedx_yaml, all_results):
    """
    Checks to make sure yaml is parsable
    """
    try:
        data = yaml.safe_load(openedx_yaml)
        all_results[module_dict_key]['is_parsable'] = bool(data)
    except yaml.YAMLError:
        all_results[module_dict_key]['is_parsable'] = False

def check_owner(parsed_data, all_results):
    """ Test if owner line exists and get owner name """
    #TODO(jinder): decide how flexible do we want to be with this
    all_results[module_dict_key]['owner'] = None
    if 'owner' in parsed_data.keys():
        all_results[module_dict_key]['owner'] = parsed_data['owner']

def check_oep(parsed_data, all_results):
    """
    Checks for significant oeps info
    """
    important_oeps = [2, 7, 18, 30]
    if 'oeps' in parsed_data:
        oeps = parsed_data['oeps']
        for oep_num in important_oeps:
            oep_name = "oep-{num}".format(num=oep_num)
            if oep_name in oeps:
                all_results[module_dict_key][oep_name] = oeps[oep_name]
            else:
                all_results[module_dict_key][oep_name] = False
