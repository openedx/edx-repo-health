import os
import subprocess

import toml

from repo_health import get_file_content


def check_version_in_toml(version_type, repo_dir, version):
    """
    version_type: Django or Python
    repo_dir: repository path
    version: version to look for
    """
    # Read the pyproject.toml file
    pyproject_toml_file_path = os.path.join(repo_dir, "pyproject.toml")
    try:
        data = toml.load(get_file_content(pyproject_toml_file_path))
    except FileNotFoundError:
        return False  # File not found
    except toml.TomlDecodeError:
        return False  # Invalid TOML format

    classifiers = data.get('project', {}).get('classifiers', [])

    if version_type == "python":
        return any(f"Programming Language :: Python :: {version}" in classifier for classifier in classifiers)
    elif version_type == "django":
        dependencies = data.get('project', {}).get('dependencies', [])
        return any(f"Django=={version}" in classifier for classifier in dependencies)


def get_release_tags(repo_dir):
    try:
        subprocess.run(['git', 'fetch', '--tags'], cwd=repo_dir)
        git_tags = subprocess.check_output(['git', 'tag', '--sort=version:refname'], cwd=repo_dir, text=True)
        all_tags_list = git_tags.strip().split('\n')
        latest_tag = get_latest_release_tag(repo_dir)

        if not latest_tag and len(all_tags_list):
            return all_tags_list
        elif latest_tag and len(all_tags_list):
            return all_tags_list[:all_tags_list.index(latest_tag) + 1]
        else:
            return None
    except Exception as ex:
        print(str(ex))
        return None


def get_latest_release_tag(repo_dir):
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
    # Get the symbolic reference for the remote's HEAD
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
    subprocess.run(['git', 'checkout', tag], cwd=repo_dir)
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
    if check_version_in_toml("django", repo_dir, version):
        return True
    return False


def find_python_version_in_config_files(repo_dir, tag, version):
    subprocess.run(['git', 'checkout', tag], cwd=repo_dir)
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
    if check_version_in_toml("python", repo_dir, version):
        return True
    return False


def is_django_package(repo_dir):
    setup_files = ['setup.py', 'setup.cfg']

    for setup_file in setup_files:
        file_path = os.path.join(repo_dir, setup_file)
        if os.path.exists(file_path):
            if "'Framework :: Django" in get_file_content(file_path):
                return True

    return False
