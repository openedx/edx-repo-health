import os
import pytest

from repo_health.check_openedx_yaml import (
    check_obsolete_fields,
    check_oeps,
    check_release_maybe,
    check_release_org_compliance,
    check_release_ref,
    check_yaml_parsable,
    fixture_oeps,
    fixture_openedx_yaml,
    fixture_parsed_data,
    module_dict_key,
    obsolete_fields,
    output_keys,
)


def get_repo_path(repo_name):
    tests_directory = os.path.dirname(__file__)
    return f"{tests_directory}/fake_repos/{repo_name}"


@pytest.mark.parametrize("repo_path, result", [
    (get_repo_path("openedx_repo1"), "master"),
    (get_repo_path("openedx_repo2"), ""),
])
def test_check_release_ref(parsed_data, result):
    all_results = {module_dict_key:{}}
    check_release_ref(parsed_data, all_results)

    assert all_results[module_dict_key]['release'] == result


@pytest.mark.parametrize("repo_path, result", [
    (get_repo_path("openedx_repo1"), True),
    (get_repo_path("openedx_repo2"), False),
])
def test_check_release_maybe(parsed_data, result):
    all_results = {module_dict_key:{}}
    check_release_maybe(parsed_data, all_results)

    assert all_results[module_dict_key]['release-maybe'] == result


@pytest.mark.parametrize("repo_path, git_origin_url, result", [
    (get_repo_path("openedx_repo1"), "https://github.com/openedx/openedx_repo1.git", True),
    (get_repo_path("openedx_repo2"), "https://github.com/openedx/openedx_repo2.git", True),
    (get_repo_path("openedx_repo3"), "https://github.com/edx/openedx_repo3.git", False),
])
def test_check_release_org_compliance(parsed_data, git_origin_url, result):
    all_results = {module_dict_key:{}}
    check_release_org_compliance(parsed_data, git_origin_url, all_results)
    assert all_results[module_dict_key]["release-org-compliance"] == result


@pytest.mark.parametrize("repo_path, result", [
    (get_repo_path("openedx_repo1"), True),
    (get_repo_path("openedx_repo2"), True),
    (get_repo_path("docs_repo"), False),
])
def test_check_yaml_parsable(openedx_yaml, result):
    all_results = {module_dict_key:{}}
    check_yaml_parsable(openedx_yaml, all_results)

    assert all_results[module_dict_key]['parsable'] == result


@pytest.mark.parametrize("repo_path, result_list", [
    (get_repo_path("openedx_repo1"), {
        "oep-2":True,
        "oep-7":False,
        "oep-18":True,
        "oep-30":False
    }),
    (get_repo_path("openedx_repo2"), {
        "oep-2":True,
        "oep-7":True,
        "oep-18":False,
        "oep-30":False
    }),
])
def test_check_oeps(oeps, result_list):
    all_results = {module_dict_key:{}}
    check_oeps(oeps, all_results)

    for key, desc in output_keys.items():
        assert all_results[module_dict_key][key] == result_list[key]


@pytest.mark.parametrize("repo_path, result_list", [
    (get_repo_path("openedx_repo1"), ["nick"]),
    (get_repo_path("openedx_repo2"), ["nick", "supporting-teams"]),
])
def test_check_obsolete_fields(parsed_data, result_list):
    all_results = {module_dict_key:{}}
    check_obsolete_fields(parsed_data, all_results)

    for field in all_results[module_dict_key]['obsolete_fields'].split():
        assert field in result_list
