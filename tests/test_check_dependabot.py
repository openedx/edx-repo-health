"""Test suite for dependabot check"""

import pytest
from repo_health import get_file_content

from repo_health.check_dependabot import (
    check_dependabot_exists, 
    check_has_ecosystems, 
    module_dict_key, 
    dependabot_path
)


@pytest.fixture(name="dependabot_yml")
def fixture_dependabot_yml():
    """Fixture containing the text content of dependabot.yml"""
    return get_file_content(dependabot_path)


def test_check_dependabot_exists(dependabot_yml):
    """
    Test to check if the result are either True or False
    """
    all_results = {module_dict_key: {}}
    check_dependabot_exists(dependabot_yml, all_results)

    assert type(all_results[module_dict_key]['exists']) == bool


def test_check_dependabot_alerts_openedx(dependabot_yml):
    """
    Test to check if all has_ecosystem values are eitheer True or False
    """
    all_results = {module_dict_key: {}}
    ecosystems = ["pip", "npm", "github-actions"]
    check_has_ecosystems(dependabot_yml, all_results)

    for ecosystem in ecosystems:
        assert type(all_results[module_dict_key]["has_ecosystem"][ecosystem]) == bool
