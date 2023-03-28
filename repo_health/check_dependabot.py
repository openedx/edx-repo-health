"""
Checks to make suree dependabot files are there and they have enough ecosystems
"""
from ruamel.yaml import YAML

import pytest
from pytest_repo_health import add_key_to_metadata, health_metadata
from repo_health import get_file_content

module_dict_key = "dependabot"
dependabot_path=".github/dependabot.yml"


@pytest.fixture(name="dependabot_yml")
def fixture_dependabot_yml():
    """Fixture containing the text content of dependabot.yml"""
    return get_file_content(dependabot_path)


@add_key_to_metadata((module_dict_key, "exists"))
def check_dependabot_exists(dependabot_yml, all_results):
    """
    Is dependabot.yml file exists
    """
    all_results[module_dict_key]["exists"] = bool(dependabot_yml)


@health_metadata(
    [module_dict_key, "has_ecosystem"],
    {
        "github_action": "ecosystem to check github actions version upgrades",
        "pip": "ecosystem to check pip package version upgrades",
        "npm": "ecosystem to check node package version upgrades"
    },
)
def check_has_ecosystems(dependabot_yml, all_results):
    """
    Is dependabot.yml has github_action, pip, npm ecosystems/sections
    """
    ecosystems = ["pip", "npm", "github-actions"]
    all_results[module_dict_key]["has_ecosystem"] = {}
    if dependabot_yml:
        dependabot_elements = []
        yml_instance = YAML()
        yml_instance.preserve_quotes = True
        yml_instance.default_flow_style = None
        yml_instance.indent(mapping=2, sequence=2, offset=0)
        with open(dependabot_path) as file_stream:
            dependabot_elements = yml_instance.load(file_stream)
        dependabot_elements['updates'] = dependabot_elements.get('updates') or []

        for ecosystem in ecosystems:
            found = False
            for index in dependabot_elements['updates']:
                if ecosystem == index.get('package-ecosystem'):
                    found = True
            all_results[module_dict_key]["has_ecosystem"][ecosystem] = found

