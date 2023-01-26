"""
Checks to see if openedx.yaml follows minimum standards
And gathers info
"""

import os

import pytest
import yaml

from pytest_repo_health import add_key_to_metadata, health_metadata

from repo_health import get_file_content

from .utils import github_org_repo

# Decision: require openedx.yaml to be parsable

module_dict_key = "openedx_yaml"
output_keys = {
    "oep-2": "Indicates compliance with OEP-2: standards for how openedx.yaml is structured",
    "oep-7": "Indicates compliance with OEP-7: has repo migrated to python 3?",
    "oep-18": "Indicates compliance with OEP-18: standards for make upgrade target and requirement files",
    "oep-30": "Indicates compliance with OEP-30: Personally Identifiable Information Markup and Auditing",
}

obsolete_fields = ['nick', 'owner', 'supporting_teams', 'track_pulls', 'track-pulls']


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


@health_metadata([module_dict_key], output_keys)
def check_obsolete_fields(parsed_data, all_results):
    """
    Report presence of obsolete fields
    """
    obsolete_fields_in_file = [field for field in obsolete_fields if field in parsed_data]
    all_results[module_dict_key]["obsolete_fields"] = ",".join(obsolete_fields_in_file)


@add_key_to_metadata((module_dict_key, "release"))
def check_release_ref(parsed_data, all_results):
    """
    Is this repo tagged as part of Open edX releases?
    """
    ref = parsed_data.get("openedx-release", {}).get("ref", "")
    all_results[module_dict_key]["release"] = ref


@add_key_to_metadata((module_dict_key, "release-maybe"))
def check_release_maybe(parsed_data, all_results):
    """
    Does this repo still have "maybe" for openedx-release? True is bad.
    """
    maybe = parsed_data.get("openedx-release", {}).get("maybe", False)
    all_results[module_dict_key]["release-maybe"] = maybe


@add_key_to_metadata((module_dict_key, "release-org-compliance"))
def check_release_org_compliance(parsed_data, git_origin_url, all_results):
    """
    Does this repo comply with the rule that Open edX components must be in the
    openedx GitHub org? False is bad.
    """
    maybe = parsed_data.get("openedx-release", {}).get("maybe", False)
    ref = parsed_data.get("openedx-release", {}).get("ref", "")
    if ref and not maybe:
        org_name, _ = github_org_repo(git_origin_url)
        good_org = (org_name == "openedx")
    else:
        good_org = True
    all_results[module_dict_key]["release-org-compliance"] = good_org
