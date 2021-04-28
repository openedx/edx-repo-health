import os

from repo_health.check_dependencies import DependencyReader, get_dependencies


def get_repo_path(repo_name):
    tests_directory = os.path.dirname(__file__)
    return f"{tests_directory}/{repo_name}"


def test_python_js_repo_dependency_check():
    repo_path = get_repo_path('fake_repos/python_js_repo')
    dependencies = get_dependencies(repo_path)

    assert 'fs==2.0.18' in dependencies.get("pypi").get("list")
    assert "react-redux" in dependencies.get("js").get("list").keys()
    assert dependencies.get("count") == 350
    assert dependencies.get("pypi").get("count") == 299
    assert dependencies.get("github").get("count") == 14
    assert dependencies.get("js").get("count") == 37


def test_js_repo_dependency_check():
    repo_path = get_repo_path('fake_repos/js_repo')
    dependencies = get_dependencies(repo_path)

    assert 'core-js' in dependencies.get("js").get("list").keys()
    assert dependencies.get("count") == 37
    assert len(dependencies.get("js").get("list")) == 26
    assert len(dependencies.get("js").get("dev.List")) == 11
    assert dependencies.get("pypi").get("count") == 0


def test_python_repo_dependency_check():
    repo_path = get_repo_path('fake_repos/python_repo')
    dependencies = get_dependencies(repo_path)

    assert 'six==1.15.0' in dependencies.get("pypi").get("list")
    assert dependencies.get("count") == 65
    assert dependencies.get("pypi").get("count") == 65
    assert dependencies.get("github").get("count") == 0
    assert dependencies.get("js").get("count") == 0
