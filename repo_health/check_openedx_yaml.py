"""
Checks to see if openedx.yaml follows minimum standards
And gathers info
"""
import os
import pytest
import yaml

from pytest_repo_health import add_key_to_metadata, health_metadata

from repo_health import get_file_content

# Decision: require openedx.yaml to be parsable

module_dict_key = "openedx_yaml"
output_keys = {
    "oep-2": "Indicates compliance with OEP-2: standards for how openedx.yaml is structured",
    "oep-7": "Indicates compliance with OEP-7: has repo migrated to python 3?",
    "oep-18": "Indicates compliance with OEP-18: standards for make upgrade target and requirement files",
    "oep-30": "Indicates compliance with OEP-30: Personally Identifiable Information Markup and Auditing",
}


@pytest.fixture(name='openedx_yaml')
def fixture_openedx_yaml(repo_path):
    """Fixture containing the text content of openedx.yaml"""
    full_path = os.path.join(repo_path, "openedx.yaml")
    return get_file_content(full_path)


@pytest.fixture(name='parsed_data')
def fixture_parsed_data(openedx_yaml):
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
        all_results[module_dict_key]["parsable"] = bool(data)
    except yaml.YAMLError:
        all_results[module_dict_key]["parsable"] = False


@pytest.fixture(name='oeps')
def fixture_oeps(parsed_data):
    if "oeps" in parsed_data:
        return parsed_data["oeps"]
    return {}


@health_metadata(
    [module_dict_key],
    output_keys
)
def check_oeps(oeps, all_results):
    """
    Check compliance with OEPs of particular interest
    """
    for oep_name, _ in output_keys.items():
        value = False
        if oep_name in oeps:
            oep = oeps[oep_name]
            if isinstance(oep, bool):
                value = oep
            elif "state" in oep:
                value = oep["state"]
        all_results[module_dict_key][oep_name] = value
