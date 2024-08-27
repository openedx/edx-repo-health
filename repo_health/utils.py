"""
Utility Functions
"""
import functools
import operator
import os
import re
import subprocess
from datetime import datetime

import toml

from repo_health import get_file_content

GITHUB_DATETIME_FMT = "%Y-%m-%dT%H:%M:%SZ"
URL_PATTERN = r"github.com[/:](?P<org_name>[^/]+)/(?P<repo_name>[^/]+).git"


def file_exists(repo_path, file_name):
    full_path = os.path.join(repo_path, file_name)
    return os.path.isfile(full_path)


def dir_exists(repo_path, dir_name):
    full_path = os.path.join(repo_path, dir_name)
    return os.path.isdir(full_path)


def parse_build_duration_response(json_response):
    """
    This function is responsible for parsing Github GraphQL API response and calculating build duration.

    Returns None when repo is uninitialized.
    """
    build_checks = []
    first_started_at = None
    last_completed_at = None
    total_duration = ''

    # Handle uninitialized repos (missing default branch, or no commits on branch)
    try:
        latest_commits = functools.reduce(
            operator.getitem, ["node", "defaultBranchRef", "target", "history", "edges"], json_response)
    except TypeError:
        return None

    if not latest_commits:
        return None
    else:
        latest_commit = latest_commits[0]

    for check_suite in functools.reduce(operator.getitem, ['node', 'checkSuites', 'edges'], latest_commit):

        all_check_runs = check_suite['node']['checkRuns']['edges']
        for check_run in all_check_runs:
            # If check is still in progress, skip it
            if not check_run['node']['completedAt']:
                continue

            name = check_run['node']['name']
            started_at = datetime.strptime(check_run['node']['startedAt'], GITHUB_DATETIME_FMT)
            completed_at = datetime.strptime(check_run['node']['completedAt'], GITHUB_DATETIME_FMT)

            if not first_started_at or started_at < first_started_at:
                first_started_at = started_at
            if not last_completed_at or completed_at > last_completed_at:
                last_completed_at = completed_at

            job_duration = completed_at - started_at
            total_seconds = job_duration.total_seconds()
            minutes, remaining_seconds = divmod(total_seconds, 60)

            build_checks.append({
                'name': name,
                'duration': f'{int(minutes)} minutes {int(remaining_seconds)} seconds',
                'seconds': total_seconds
            })

    if build_checks:
        # sorting checks into descending order of duration to get slowest check on top
        build_checks = sorted(build_checks, key=lambda k: k['seconds'], reverse=True)
        for check in build_checks:
            del check['seconds']

        build_duration = last_completed_at - first_started_at
        minutes, remaining_seconds = divmod(build_duration.total_seconds(), 60)

        total_duration = f'{int(minutes)} minutes {int(remaining_seconds)} seconds'

    return total_duration, build_checks


def github_org_repo(git_origin_url):
    """Return the org and repo from a GitHub URL."""
    match = re.search(URL_PATTERN, git_origin_url)
    assert match is not None
    return match.groups()


def find_version_in_toml(version_type, repo_dir, version):
    """
    version_type: Django or Python
    repo_dir: repository path
    version: version to look for
    """
    try:
        data = toml.load(os.path.join(repo_dir, "pyproject.toml"))
        classifiers = data.get('project', {}).get('classifiers', [])
        if version_type == "python":
            return any(f"Programming Language :: Python :: {version}" in classifier for classifier in classifiers)
        elif version_type == "django":
            dependencies = data.get('project', {}).get('dependencies', [])
            return any(f"Django=={version}" in classifier for classifier in dependencies)
        else:
            return False
    except FileNotFoundError:
        return False  # File not found
    except toml.TomlDecodeError:
        return False  # Invalid TOML format


def get_release_tags(repo_dir):
    """
    A util function which is returning all repo release tags
    """
    try:
        subprocess.run(['git', 'fetch', '--tags'], cwd=repo_dir, check=True)
        git_tags = subprocess.check_output(['git', 'tag', '--sort=version:refname'], cwd=repo_dir, text=True)
        # Filtering out empty strings or non-trivial values
        all_tags_list = [tag for tag in git_tags.strip().split('\n') if tag.strip()]
        latest_tag = get_latest_release_tag(repo_dir)

        if not latest_tag and len(all_tags_list):
            return all_tags_list
        elif latest_tag and len(all_tags_list):
            return all_tags_list[:all_tags_list.index(latest_tag) + 1]
        else:
            return None
    except Exception as ex:  # pylint: disable=broad-exception-caught
        print(str(ex))
        return None


def get_latest_release_tag(repo_dir):
    """
    A util function which returns a latest release tag
    """
    try:
        # Run the Git command to get the latest tag on the specified branch
        return subprocess.check_output(
            ["git", "describe", "--tags", "--abbrev=0", get_default_branch(repo_dir)],
            cwd=repo_dir,
            text=True
        ).strip()

    except subprocess.CalledProcessError as e:
        # Handle errors, e.g., when there are no tags on the specified branch
        print(f"Error: {e}")
        return None


def get_default_branch(repo_dir):
    """
    Get the symbolic reference for the remote's HEAD
    or default branch name
    """
    try:
        default_branch_ref = subprocess.check_output(
            ['git', 'symbolic-ref', 'refs/remotes/origin/HEAD'],
            cwd=repo_dir, text=True
        ).strip()
        # Extract the branch name
        default_branch = default_branch_ref.split('/')[-1]
        return default_branch
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        return "No Default Branch"


def find_django_version_in_setup_py_classifier(repo_dir, tag, version):
    """
    A utill function which is checking the provided python version
    in classifiers inside config files like setup.py and setup.cfg
    """
    subprocess.run(['git', 'checkout', tag], cwd=repo_dir, check=True)
    setup_py_path = os.path.join(repo_dir, 'setup.py')
    setup_cfg_path = os.path.join(repo_dir, 'setup.cfg')

    if not os.path.exists(setup_py_path):
        setup_py_path = None
    if not os.path.exists(setup_cfg_path):
        setup_cfg_path = None

    if setup_py_path:
        if f"Framework :: Django :: {version}" in get_file_content(setup_py_path):
            return True
    if setup_cfg_path:
        if f"Framework :: Django :: {version}" in get_file_content(setup_cfg_path):
            return True
    if find_version_in_toml("django", repo_dir, version):
        return True
    return False


def find_python_version_in_config_files(repo_dir, tag, version):
    """
    A utill function which is checking the provided python version
    in config files like setup.py and setup.cfg
    """
    subprocess.run(['git', 'checkout', tag], cwd=repo_dir, check=True)
    setup_py_path = os.path.join(repo_dir, 'setup.py')
    setup_cfg_path = os.path.join(repo_dir, 'setup.cfg')

    if not os.path.exists(setup_py_path):
        setup_py_path = None
    if not os.path.exists(setup_cfg_path):
        setup_cfg_path = None

    if setup_py_path:
        if f"Programming Language :: Python :: {version}" in get_file_content(setup_py_path):
            return True
    if setup_cfg_path:
        if f"Programming Language :: Python :: {version}" in get_file_content(setup_cfg_path):
            return True
    if find_version_in_toml("python", repo_dir, version):
        return True
    return False


def is_django_package(repo_dir):
    """
    A util function that checks if it is Django package
    """
    setup_files = ['setup.py', 'setup.cfg']

    for setup_file in setup_files:
        file_path = os.path.join(repo_dir, setup_file)
        if os.path.exists(file_path):
            if "'Framework :: Django" in get_file_content(file_path):
                return True

    return False
