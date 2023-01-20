import json
import os

import pytest
import responses

from repo_health.check_docs import ReadTheDocsChecker, check_build_bagde, check_python_version, module_dict_key


def get_repo_path(repo_name):
    tests_directory = os.path.dirname(__file__)
    return f"{tests_directory}/{repo_name}"


@pytest.mark.parametrize("fake_repo, expected_result", [
    ("read_the_docs", True),
    ("no_read_the_docs", False)])

def test_check_build_badge(fake_repo, expected_result):
    repo_path = get_repo_path('fake_repos/'+ fake_repo)
    all_results = {module_dict_key:{}}
    file = open(repo_path+'/README.rst','r')
    check_build_bagde(file.read(), all_results)

    assert all_results[module_dict_key]["build_badge"] == expected_result


@pytest.mark.parametrize("fake_repo, expected_result", [
    ("read_the_docs",3.8),
    ("no_read_the_docs",None)])

def test_check_python_version(fake_repo, expected_result):
    repo_path = get_repo_path('fake_repos/'+ fake_repo)
    all_results = {module_dict_key:{}}
    check_python_version(repo_path, all_results)

    assert all_results[module_dict_key]["python_version"] == expected_result

@responses.activate

def test_check_readthedocs_build_success():

    current_dir = os.path.dirname(__file__)
    projects_data = open(os.path.join(current_dir, 'data/readthedocs_projects.json'), 'r')
    responses.add(responses.GET, 'https://readthedocs.org/api/v3/projects/?limit=100',
                  json= json.load(projects_data))

    builds_data = open(os.path.join(current_dir, 'data/readthedocs_builds_success.json'),'r')
    responses.add(responses.GET, "https://readthedocs.org/api/v3/projects/testing-demo/builds/",
                  json= json.load(builds_data))

    checker = ReadTheDocsChecker(git_origin_url="https://github.com/readthedocs/readthedocs.git", token='token')
    checker.update_build_details()

    all_results = {module_dict_key: {}}
    all_results[module_dict_key]["build_details"] = json.dumps(checker.build_details)

    assert all_results[module_dict_key]["build_details"] == '[{"project": "testing-demo", "last_build_status": "success", "last_build_time": "2021-06-11T12:31:31.357860Z", "last_good_build_time": "2021-06-11T12:31:31.357860Z"}]'

@responses.activate

def test_check_readthedocs_build_failure():

    current_dir = os.path.dirname(__file__)
    projects_data = open(os.path.join(current_dir, 'data/readthedocs_projects.json'), 'r')
    responses.add(responses.GET, 'https://readthedocs.org/api/v3/projects/?limit=100',
                  json= json.load(projects_data))

    builds_data = open(os.path.join(current_dir, 'data/readthedocs_builds_failure.json'),'r')
    responses.add(responses.GET, "https://readthedocs.org/api/v3/projects/testing-demo/builds/",
                  json= json.load(builds_data))

    checker = ReadTheDocsChecker(git_origin_url="https://github.com/readthedocs/readthedocs.git", token='token')
    checker.update_build_details()

    all_results = {module_dict_key: {}}
    all_results[module_dict_key]["build_details"] = json.dumps(checker.build_details)

    assert all_results[module_dict_key]["build_details"] == '[{"project": "testing-demo", "last_build_status": "failure", "last_build_time": "2021-06-11T12:31:31.357860Z", "last_good_build_time": "2021-03-12T20:36:20.239344Z"}]'
