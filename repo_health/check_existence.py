"""
Functions to check the existence of files.
"""

from pytest_repo_health import health_metadata

from .utils import dir_exists, file_exists


module_dict_key = "exists"

req_files = {
    "openedx.yaml": "openedx.yaml contains repository metadata as outlined in OEP-2",
    "Makefile": "Make targets",
    "tox.ini": "Tox configuration",
    ".travis.yml": "Travis configuration",
    "CHANGELOG.rst": "Change history",
    "pylintrc": "Pylint configuration",
    "setup.cfg": "Application setup configuration",
    "setup.py": "Application setup",
    ".coveragerc": "Test coverage configuration",
    ".editorconfig": "IDE configuration",
    ".pii_annotations.yml": "PII annotations as outline in OEP-0030",
    ".gitignore": "git ignore configuration",
    "package.json": "packages managed by npm",
    "transifex_config": "transifex config file",
}

req_dirs = {
    "requirements": "separate folder for requirement files",
}

req_paths = [
    # Tuple is path-to-file, key-name, description.
    (".github/workflows/commitlint.yml", "commitlint.yml", "GitHub Action to check conventional commits"),
    (".github/dependabot.yml", "dependabot.yml", "GitHub Action to check dependabot"),
]


@health_metadata(
    [module_dict_key],
    req_files
)
def check_file_existence(repo_path, all_results):
    """
    Checks repository contains file which is not empty at root level
    """
    for file_name, _ in req_files.items():
        all_results[module_dict_key][file_name] = file_exists(
            repo_path, file_name
        )


@health_metadata(
    [module_dict_key],
    req_dirs
)
def check_dir_existence(repo_path, all_results):
    """
    Checks whether repository contains required folders at root level
    """
    for dir_name, _ in req_dirs.items():
        all_results[module_dict_key][dir_name] = dir_exists(
            repo_path, dir_name
        )


@health_metadata(
    [module_dict_key],
    {key: desc for _, key, desc in req_paths},
)
def check_path_existence(repo_path, all_results):
    """
    Checks whether the repo contains required files at deep levels.
    """
    for file_path, key, _ in req_paths:
        exists = file_exists(repo_path, file_path)
        all_results[module_dict_key][key] = exists


@health_metadata(
    [module_dict_key],
    {"README": "Basic level of documentation in the form of README.rst or README.md"}
)
def check_readme_existence(repo_path, all_results):
    """
    Check if README exists in repository.
    """
    exists = any(file_exists(repo_path, file) for file in ['README.rst', 'README.md'])

    all_results[module_dict_key]['README'] = exists


@health_metadata(
    [module_dict_key],
    {"transifex_config": "transifex config file"}
)
def check_transifex_config_existence(repo_path, all_results):
    """
    Check if transifex config exists in repository.
    """
    exists = file_exists(repo_path, '.tx/config')
    all_results[module_dict_key]['transifex_config'] = exists
