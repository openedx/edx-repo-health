import os

from repo_health.check_ubuntufiles import get_apt_get_txt, get_docker_file_content


def get_repo_path(repo_name):
    tests_directory = os.path.dirname(__file__)
    return f"{tests_directory}/{repo_name}"


def test_loading_docker_file_check():
    repo_path = get_repo_path('fake_repos/python_repo')
    dependencies = get_docker_file_content(repo_path)
    assert 'apt-get install' in dependencies
    assert 'apt-get update' in dependencies
    assert 'python3-pip' in dependencies
    assert 'libssl-dev' in dependencies


def test_no_docker_file_check():
    repo_path = get_repo_path('fake_repos/docs_repo')
    assert get_docker_file_content(repo_path) is None


def test_empty_docker_file_check():
    repo_path = get_repo_path('fake_repos/kodejail')
    assert get_docker_file_content(repo_path) is None


def test_docker_new_format():
    repo_path = get_repo_path('fake_repos/python_js_repo')
    dependencies = get_docker_file_content(repo_path)
    assert 'apt-get install' in dependencies
    assert 'apt-get update' in dependencies
    assert 'git-core' in dependencies
    assert 'curl' in dependencies


def test_loading_apt_packages_txt():
    repo_path = get_repo_path('fake_repos/python_repo')
    dependencies = get_apt_get_txt(repo_path)
    assert 'curl' in dependencies


def test_loading_apt_packages_txt_root_path():
    repo_path = get_repo_path('fake_repos/python_js_repo')
    dependencies = get_apt_get_txt(repo_path)
    assert 'python-numpy' in dependencies


def test_not_available_apt_packages_txt():
    repo_path = get_repo_path('fake_repos/js_repo')
    dependencies = get_apt_get_txt(repo_path)
    assert dependencies == []
