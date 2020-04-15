"""
Checks to see if openedx.yaml follows minimum standards
And gathers info
"""
import pytest
import yaml
import os

from pytest_repo_health import add_key_to_metadata

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

@add_key_to_metadata((module_dict_key, "parsable"))
def check_yaml_parsable(openedx_yaml, all_results):
    """
    Is the openedx.yaml file computer parsable
    """
    try:
        data = yaml.safe_load(openedx_yaml)
        all_results[module_dict_key]['parsable'] = bool(data)
    except yaml.YAMLError:
        all_results[module_dict_key]['parsable'] = False

@add_key_to_metadata((module_dict_key, "owner"))
def check_owner(parsed_data, all_results):
    """
    The name of official owner of repo(the one reponsible for maintenance)
    """
    all_results[module_dict_key]['owner'] = None
    if 'owner' in parsed_data.keys():
        all_results[module_dict_key]['owner'] = parsed_data['owner']

@add_key_to_metadata((module_dict_key, "oep_2"))
def check_oep_2(parsed_data, all_results):
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

@pytest.fixture
def oeps(parsed_data):
    if 'oeps' in parsed_data:
        return parsed_data['oeps']
    return {}

@add_key_to_metadata((module_dict_key, "oep_2"))
def check_oep_2(oeps, all_results):
    """
    Indicated compliance with OEP-2: standards for how openedx.yaml is structured
    """
    oep_name = "oep-2"
    if oep_name in oeps:
        all_results[module_dict_key][oep_name] = oeps[oep_name]
    else:
        all_results[module_dict_key][oep_name] = False

@add_key_to_metadata((module_dict_key, "oep_2"))
def check_oep_7(oeps, all_results):
    """
    Indicates compliance with OEP-7: has repo migrated to python 3
    """
    oep_name = "oep-7"
    if oep_name in oeps:
        all_results[module_dict_key][oep_name] = oeps[oep_name]
    else:
        all_results[module_dict_key][oep_name] = False

@add_key_to_metadata((module_dict_key, "oep_18"))
def check_oep_18(oeps, all_results):
    """
    Indicates compliance with OEP-18: standards for make upgrade target and requirement files
    """
    oep_name = "oep-18"
    if oep_name in oeps:
        all_results[module_dict_key][oep_name] = oeps[oep_name]
    else:
        all_results[module_dict_key][oep_name] = False

@add_key_to_metadata((module_dict_key, "oep_30"))
def check_oep_18(oeps, all_results):
    """
    Indicates compliance with OEP-30: Personally Identifiable Information Markup and Auditing
    """
    oep_name = "oep-30"
    if oep_name in oeps:
        all_results[module_dict_key][oep_name] = oeps[oep_name]
    else:
        all_results[module_dict_key][oep_name] = False