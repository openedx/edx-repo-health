import os

from repo_health.check_npm_package import check_npm_package, get_dependencies, module_dict_key


def get_repo_path(repo_name):
    tests_directory = os.path.dirname(__file__)
    return f"{tests_directory}/{repo_name}"


def test_valid_npm_package_name():
    repo_path = get_repo_path('fake_repos/js_repo')
    dependencies = get_dependencies(repo_path)
    all_results = {module_dict_key: {}}
    check_npm_package(dependencies, all_results)

    assert all_results["npm_package"] == '@edx/fakename@1.1.0'


def test_invalid_npm_package_name():
    repo_path = get_repo_path('fake_repos/python_js_repo')
    dependencies = get_dependencies(repo_path)
    all_results = {module_dict_key: {}}
    check_npm_package(dependencies, all_results)
    assert all_results["npm_package"] == ''


def test_no_package_name():
    repo_path = get_repo_path('fake_repos/just_setup_py')
    dependencies = get_dependencies(repo_path)
    all_results = {module_dict_key: {}}
    check_npm_package(dependencies, all_results)
    assert all_results["npm_package"] == ''
