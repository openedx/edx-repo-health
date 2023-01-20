import os
import re

import pytest

from repo_health.check_ubuntufiles import VARIABLE_PATTERN, PlaybookAPTPackagesReader


def get_repo_path(repo_name):
    tests_directory = os.path.dirname(__file__)
    return f"{tests_directory}/{repo_name}"


def test_playbooks_apt_reader():
    repo_path = get_repo_path('fake_repos/configuration')
    reader = PlaybookAPTPackagesReader(repo_path)
    reader.update_packages_from_playbooks()
    config_yaml_data = reader.packages_from_playbooks

    assert 'apparmor-utils' in config_yaml_data["edxapp"]
    assert 'python3.8-distutils' in config_yaml_data["edxapp"]
    assert 'curl' in config_yaml_data["edxapp"]
    assert len(config_yaml_data["edxapp"]) == 13

    assert 'mongodb-org-shell=4.0.22' in config_yaml_data["mongo_4_0"]
    assert 'mongodb-org=4.0.22' in config_yaml_data["mongo_4_0"]
    assert 'jq' in config_yaml_data["mongo_4_0"]
    assert len(config_yaml_data["mongo_4_0"]) == 6


@pytest.mark.parametrize("variable, expected", [
    ("{{ debian_pkgs }}", True),
    ("{{ debian_pkgs + focal_only_pkgs }}", True),
    ("{{','.join(openstack_debian_pkgs)}}", True),
    ("debian_pkgs", False),
    ("{{ debian_pkgs", False),
    ("debian_pkgs }}", False),
])
def test_variable_pattern_regex(variable, expected):
    match = re.match(VARIABLE_PATTERN, variable)
    assert bool(match) is expected


@pytest.mark.parametrize("variable, expected", [
    ("{{ debian_pkgs }}", ["debian_pkgs", None]),
    ("{{ debian_pkgs + focal_only_pkgs }}",  ["debian_pkgs", "focal_only_pkgs"]),
    ("{{','.join(openstack_debian_pkgs)}}", ["openstack_debian_pkgs", None]),
    ("debian_pkgs", [None, None]),
    ("{{ debian_pkgs", [None, None]),
])
def test_variable_pattern_regex_groups(variable, expected):
    match = re.match(VARIABLE_PATTERN, variable)
    variables = [match['var_name'] if match else None, match['var2_name'] if match else None]
    assert variables == expected
