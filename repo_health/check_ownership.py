import os
import pytest
import yaml

from pytest_repo_health import health_metadata
from repo_health import get_file_content


module_dict_key = "ownership"


@health_metadata(
    [module_dict_key],
    {
        ("component_type"): "Type of component",
        ("name"): "Name of the component",
        ("url"): "Link to the component",
        ("theme"): "Theme that owns the component",
        ("squad"): "Squad that owns the component",
        ("priority"): "Business criticality of the component",
        ("description"): "Description of the what the component is",
        ("notes"): "Notes maintained by the owner",
    },
)
def check_ownership(repo_path, all_results):
    """
    Test to find whether repo requires some key requirements
    """
    ownership = yaml.safe_load(get_file_content(os.path.join(repo_path, ".ownership.yaml")))
    for key, value in ownership.items():
        if key == 'children':
            continue
        all_results[module_dict_key][key] = value


