import os

from repo_health.check_ubuntufiles import get_docker_file_content


def get_repo_path(repo_name):
    tests_directory = os.path.dirname(__file__)
    return f"{tests_directory}/{repo_name}"


def test_loading_docker_file_check():
    repo_path = get_repo_path('fake_repos/python_repo')
    dependencies = get_docker_file_content(repo_path)
    assert 'apt-get install' in dependencies['docker']
    assert 'apt-get update' in dependencies['docker']
    assert 'python3-pip' in dependencies['docker']
    assert 'libssl-dev' in dependencies['docker']


def test_no_docker_file_check():
    repo_path = get_repo_path('fake_repos/docs_repo')
    assert get_docker_file_content(repo_path) is None


def test_empty_docker_file_check():
    repo_path = get_repo_path('fake_repos/kodejail')
    assert get_docker_file_content(repo_path) is None


def test_docker_new_format():
    repo_path = get_repo_path('fake_repos/python_js_repo')
    dependencies = get_docker_file_content(repo_path)
    assert 'apt-get install' in dependencies['docker']
    assert 'apt-get update' in dependencies['docker']
    assert 'git-core' in dependencies['docker']
    assert 'curl' in dependencies['docker']
