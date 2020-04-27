import os

import pytest
from pytest_repo_health import add_key_to_metadata
from repo_health import get_file_content


module_dict_key = "exists"

def file_exists(repo_path, file_name):
    full_path = os.path.join(repo_path, file_name)
    return bool(get_file_content(full_path))

@add_key_to_metadata((module_dict_key, "openedx.yaml"))
def check_openedx_yaml(repo_path, all_results):
    """
    openedx.yaml should contain repository metadata as outlined in OEP-2
    
    https://open-edx-proposals.readthedocs.io/en/latest/oep-0002-bp-repo-metadata.html
    """
    all_results[module_dict_key]['openedx.yaml'] = file_exists(repo_path, 'openedx.yaml')

@add_key_to_metadata((module_dict_key, "Makefile"))
def check_makefile(repo_path, all_results):
    """
    A repo should contain a makefile with various targets for working with repo
    """
    all_results[module_dict_key]['Makefile'] = file_exists(repo_path, 'Makefile')


@add_key_to_metadata((module_dict_key, "tox.ini"))
def check_tox_ini(repo_path, all_results):
    """
    Does this repo use tox to run tests in multiple environments
    """
    all_results[module_dict_key]['tox.ini'] = file_exists(repo_path, 'tox.ini')

@add_key_to_metadata((module_dict_key, ".travis.yml"))
def check_travis_yml(repo_path, all_results):
    """
    TODO(jinder)
    """
    all_results[module_dict_key]['.travis.yml'] = file_exists(repo_path, '.travis.yml')

#TODO(jinder): add check for req files

@add_key_to_metadata((module_dict_key, "README.rst"))
def check_readme_rst(repo_path, all_results):
    """
    does repo have readme file: contains information about repo purpose and development guide
    """
    all_results[module_dict_key]['README.rst'] = file_exists(repo_path, 'README.rst')

@add_key_to_metadata((module_dict_key, "CHANGELOG.rst"))
def check_changelog_rst(repo_path, all_results):
    """
    Changelog.rst should be used to document any changes made to repo
    """
    all_results[module_dict_key]['CHANGELOG.rst'] = file_exists(repo_path, 'CHANGELOG.rst')


@add_key_to_metadata((module_dict_key, "pylintrc"))
def check_pylintrc(repo_path, all_results):
    """
    Edx has a standardized pylint errors that should be used with all edx python repos
    """
    all_results[module_dict_key]['pylintrc'] = file_exists(repo_path, 'pylintrc')

@add_key_to_metadata((module_dict_key, "setup.cfg"))
def check_setup_cfg(repo_path, all_results):
    """
    TODO(jinder)
    """
    all_results[module_dict_key]['setup.cfg'] = file_exists(repo_path, 'setup.cfg')

@add_key_to_metadata((module_dict_key, "setup.py"))
def check_setup_py(repo_path, all_results):
    """
    TODO(jinder)
    """
    all_results[module_dict_key]['setup.py'] = file_exists(repo_path, 'setup.py')

@add_key_to_metadata((module_dict_key, ".coveragerc"))
def check_coveragerc(repo_path, all_results):
    """
    TODO(jinder)
    """
    all_results[module_dict_key]['.coveragerc'] = file_exists(repo_path, '.coveragerc')

@add_key_to_metadata((module_dict_key, ".editorconfig"))
def check_editorconfig(repo_path, all_results):
    """
    TODO(jinder)
    """
    all_results[module_dict_key]['.editorconfig'] = file_exists(repo_path, '.editorconfig')

@add_key_to_metadata((module_dict_key, ".pii_annotations.yml"))
def check_pii_annotations_yml(repo_path, all_results):
    """
    TODO(jinder)
    """
    all_results[module_dict_key]['.pii_annotations.yml'] = file_exists(repo_path, '.pii_annotations.yml')

@add_key_to_metadata((module_dict_key, ".gitignore"))
def check_gitignore(repo_path, all_results):
    """
    TODO(jinder)
    """
    all_results[module_dict_key]['.gitignore'] = file_exists(repo_path, '.gitignore')

