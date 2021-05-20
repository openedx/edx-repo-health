import os

from repo_health.check_ubuntufiles import get_apt_get_txt, get_docker_file_content


def get_repo_path(repo_name):
    tests_directory = os.path.dirname(__file__)
    return f"{tests_directory}/{repo_name}"


def test_loading_docker_file_check():
    repo_path = get_repo_path('fake_repos/python_repo')
    dependencies = get_docker_file_content(repo_path)
    assert 'libssl-dev' in dependencies
    for data in ['git-core', 'language-pack-en', 'python3.8', 'python3-pip', 'libssl-dev']:
        assert data in dependencies


def test_no_docker_file_check():
    repo_path = get_repo_path('fake_repos/docs_repo')
    assert get_docker_file_content(repo_path) is None


def test_empty_docker_file_check():
    repo_path = get_repo_path('fake_repos/kodejail')
    assert get_docker_file_content(repo_path) is None


def test_docker_different_format():
    repo_path = get_repo_path('fake_repos/python_js_repo')
    dependencies = get_docker_file_content(repo_path)
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
