"""
Checks Dockerfile in the repo, and try to parse out packages installed via apt-get install and update.
Also check the apt-packages.txt content.
"""
import glob
import json
import logging
import os
import re
from pathlib import Path

import pytest
import yaml

from pytest_repo_health import health_metadata

from repo_health import get_file_lines, read_docker_file

from .utils import github_org_repo

module_dict_key = "ubuntu_packages"

logger = logging.getLogger(__name__)

# pylint: disable=line-too-long
# Pattern to extract variable names from anisble template variables
VARIABLE_PATTERN = r"{{\s*?(?:[\"']\s?,[\"']\.join\(\s?)?(?P<var_name>[^\W0-9]\w*)\[?(?P<var1_index>[^\W0-9]\w*)?\]?\s?\)?\s*?(\s*\+\s*(?P<var2_name>[^\W0-9]\w*)(\[(?P<var2_index>[^\W0-9]\w*)\]?)?)?\s*}}"


def get_docker_file_content(repo_path):
    """
   entry point to parse docker file and do cleaning.
   @param repo_path:
   @return: json data
   """
    content = None

    for file in ['Dockerfile', 'Dockerfile-testing', 'Dockerfile-3.8']:
        full_path = os.path.join(repo_path, file)
        if os.path.exists(full_path):
            content = read_docker_file(full_path)
            if content:
                break

    if not content:
        return None

    lists = []

    for con in content:
        fir, sec = False, False
        if 'RUN apt-get update' in con.original:
            lists.append(clean_data(con.original))
            fir = True
        if 'RUN apt-get install' in con.original:
            lists.append(clean_data(con.original))
            sec = True
        if fir and sec:  # no need to iterate after getting req data.
            break

    ignored_list = ['chmod', '/usr/local/bin/gosu', '-qqy', '/usr/bin/python3', '/usr/bin/pip', 'then', '-sf']
    return list({item for sublist in lists for item in sublist if item not in ignored_list and len(item) > 2})


class PlaybookAPTPackagesReader:
    """
    Class containing all the utilities to read/parse Ubuntu packages in ansible playbooks
    """

    def __init__(self, repo_path):
        self.repo_path = repo_path
        self.packages_from_playbooks = {}
        self.playbook_dirs = ["playbooks/roles"]
        self._loop_keys = ["with_items", "with_list", "with_together", "with_flattened", "with_dict", "with_nested"]
        self._apt_keys = ['name', 'pkg']
        self.data_yml = None

    def _get_dirs_from_source(self, source):
        """
        Gets all playbook directories from provided source directory
        @param source: directory from which playbooks needs to be extracted
        @return: list of playbooks extracted
        """
        full_path = os.path.join(self.repo_path, source)
        return [name for name in os.listdir(full_path) if os.path.isdir(os.path.join(full_path, name))]

    def _get_data_from_playbooks(self, pattern):
        """
        Return dict containing data from all the yml files in playbook other than tasks/main.yml
        """
        self.data_yml = {}
        for file in glob.glob(pattern, recursive=True):
            with open(file, encoding="utf8") as infile:
                yml = yaml.safe_load(infile)
                if yml:
                    try:
                        self.data_yml.update(yml)
                    except ValueError as exc:
                        logger.exception("Failed to load %s with this error: %s ", file, exc)
                        continue

    def resolve_template_variable(self, node, apt_key, match):
        """
        Recursive function to replace template variables with their values
        @param node: node of tasks.yml containing apt directive
        @param apt_key: key present in current node from self._apt_keys
        @param match: re.match object
        @return: set of packages from data_yml
        """

        packages = set()
        variables = [match['var_name'] if match else None, match['var2_name'] if match else None]
        for var in variables:
            if var not in self.data_yml or not self.data_yml[var]:
                continue
            # replace placeholder with value in original string
            data = self.data_yml[var]
            if isinstance(data, str):
                _match = re.search(VARIABLE_PATTERN, data)
                if _match:
                    pkgs = self.resolve_template_variable(node, apt_key, _match)
                    for pkg in pkgs:
                        packages.add(re.sub(VARIABLE_PATTERN, pkg, match.string, count=1))
                else:
                    packages.add(re.sub(VARIABLE_PATTERN, data, match.string, count=1))
            elif isinstance(data, list):
                for item in data:
                    _match = re.search(VARIABLE_PATTERN, item)
                    if _match:
                        pkgs = self.resolve_template_variable(node, apt_key, _match)
                        for pkg in pkgs:
                            packages.add(re.sub(VARIABLE_PATTERN, pkg, match.string, count=1))
                    else:
                        packages.add(re.sub(VARIABLE_PATTERN, item, match.string, count=1))
            elif isinstance(data, set):
                packages.update(data)
        return packages

    def _get_packages_from_data_yml(self, node, apt_key):
        """
        Retrieves package from self.data_yml dict when template variable is provided in apt directive
        @param node: node of tasks.yml containing apt directive
        @param apt_key: key present in current node from self._apt_keys
        @return: set of packages from data_yml
        """
        key = next((key for key in self._loop_keys if key in node), None)
        if key is None:
            match = re.search(VARIABLE_PATTERN, node['apt'][apt_key])
            return self.resolve_template_variable(node, apt_key, match)

        if isinstance(node[key], str):
            match = re.search(VARIABLE_PATTERN, node[key])
            pkgs = self.resolve_template_variable(node, apt_key, match)
            packages = set()
            for pkg in pkgs:
                packages.add(re.sub(VARIABLE_PATTERN, pkg, node['apt'][apt_key]))
            return packages
        elif isinstance(node[key], list):
            packages = set()
            for item in node[key]:
                match = re.match(VARIABLE_PATTERN, item)
                if match:
                    pkgs = self.resolve_template_variable(node, apt_key, match)
                    for pkg in pkgs:
                        packages.add(re.sub(VARIABLE_PATTERN, pkg, node['apt'][apt_key]))
                else:
                    packages.add(item)
            return packages

        return set()

    def _replace_variable_with_data(self, package):
        """
        Replace template variable in pakcage name with its value
        @type package: package name to check if it has template variable

        """
        updated_package = ""
        while updated_package != package:
            updated_package = package
            search = re.search(VARIABLE_PATTERN, package)
            if search:
                var_name = search['var_name']
                if var_name in self.data_yml and self.data_yml[var_name]:
                    try:
                        package = re.sub(VARIABLE_PATTERN, self.data_yml[var_name], package, count=1)
                    except TypeError:
                        continue
        return updated_package

    def _prepare_data(self, packages):
        """
        Finalize the data and check if any template varaible still exists
        @type packages: list of ubuntu packages
        """
        for idx, package in enumerate(packages):
            packages[idx] = self._replace_variable_with_data(package)
        return packages

    def get_playbook_data(self, playbook_path):
        """
        Read Ubuntu packages from the provided playbook path
        @type playbook_path: path of ansible playbook
        """

        try:  # pylint: disable=too-many-nested-blocks
            # gather data from all yml files into one file"
            self._get_data_from_playbooks(f'{playbook_path}/[!tasks]*/*.yml')
            packages = set()

            for file in glob.glob(f'{playbook_path}/tasks/*.yml', recursive=True):
                full_path = os.path.join(playbook_path, file)
                with open(full_path, encoding="utf8") as target_file:
                    tasks_yml = yaml.safe_load(target_file)
                if tasks_yml is None:
                    continue

                for node in tasks_yml:
                    if "apt" in node:
                        key = next((key for key in self._apt_keys if key in node['apt']), None)
                        if key is None:
                            continue
                        try:
                            if isinstance(node['apt'][key], list):
                                packages |= set(node['apt'][key])
                            elif re.search(VARIABLE_PATTERN, node['apt'][key]):
                                items = self._get_packages_from_data_yml(node, key)
                                packages |= items
                            else:
                                packages.add(node['apt'][key])
                        except TypeError:
                            continue
            packages = self._prepare_data(list(packages))
            return packages

        except Exception as exc:  # pylint: disable=broad-except
            logger.exception("Following error occurred while parsing yml playbook (%s) in configuration repo: %s",
                             playbook_path, exc)
            return []

    def update_packages_from_playbooks(self):
        """
        Read Ubuntu packages from the all playbook paths
        """
        for source_dir in self.playbook_dirs:
            for playbook_dir in self._get_dirs_from_source(source_dir):
                packages = self.get_playbook_data(os.path.join(self.repo_path, source_dir, playbook_dir))
                self.packages_from_playbooks[playbook_dir] = packages


def get_apt_get_txt(repo_path):
    """
   entry point to parse apt-packages.txt.
   @param repo_path:
   @return: json data
   """
    full_path = os.path.join(repo_path, 'apt-packages.txt')
    # check files on root or in requirements folder
    content = get_file_lines(full_path)
    if not content:
        files = [str(file) for file in Path(os.path.join(repo_path, "requirements")).rglob('apt-packages.txt')]
        if files:
            content = get_file_lines(files[0])  # only one file will exists

    return content


def clean_data(content):
    """
    different number of spaces appearing in the content.
    Replace un-necessary information.

    :param content:
    :return: list
    """

    content = re.sub(r"\s+", ' ', content).strip()
    replace = [
        'RUN', 'apt-get update', 'apt-get install', '&&', '--yes', '-rf ', 'rm', '/var/lib/apt/lists/*',
        '--no-install-recommends', '--es', '-qy', 'upgrade', 'apt-get', '/usr/bin/pip',
        '/usr/bin/python'
    ]
    for con in replace:
        content = content.replace(con, '')

    content = content.strip().split()
    return content


@pytest.fixture(name='content')
def fixture_ubuntu_content(repo_path, git_origin_url):
    """Fixture containing the text content of dockerfile"""
    config_yaml_data = []
    _, repo_name = github_org_repo(git_origin_url)

    # Only run playbook Ubuntu packages check on configuration repo
    if repo_name == 'configuration':
        reader = PlaybookAPTPackagesReader(repo_path)
        reader.update_packages_from_playbooks()
        config_yaml_data = reader.packages_from_playbooks

    return {
        'docker_packages': get_docker_file_content(repo_path),
        'apt_get_packages': get_apt_get_txt(repo_path),
        'yml_files': json.dumps(config_yaml_data),
    }


@health_metadata(
    [module_dict_key],
    {
        "docker_packages": "content name published on ubuntu.",
        "apt_get_packages": "content name published on ubuntu.",
        "yml_files": "content name published on ubuntu.",
    })
def check_ubuntu_content(content, all_results):
    """
    Adding data into results.
    """
    for key, value in content.items():
        all_results[module_dict_key][key] = value
