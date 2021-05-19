"""
Checks Dockerfile in the repo, and try to parse out packages installed via apt-get install and update.
"""
import os
import re

import pytest
from pytest_repo_health import health_metadata

from repo_health import read_docker_file

module_dict_key = "ubuntu_packages"


def get_docker_file_content(repo_path):
    """
   entry point to read parse and read dependencies
   @param repo_path:
   @return: json data.
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

    value = []

    for con in content:
        fir, sec = False, False
        if 'RUN apt-get update' in con.original:
            value.append(clean_data(con.original))
            fir = True
        if 'RUN apt-get install' in con.original:
            value.append(clean_data(con.original))
            sec = True
        if fir and sec:  # no need to iterate after getting req data.
            break

    return {"docker": " ".join(value)}


def clean_data(content):
    """
    :param content:
    :return: different number of spaces appearing in the content. So simple clean it.
    """
    content = re.sub(r"\s+", ' ', content)
    return content


@pytest.fixture(name='content')
def fixture_ubuntu_content(repo_path):
    """Fixture containing the text content of dockerfile"""
    return get_docker_file_content(repo_path)


@health_metadata(
    [module_dict_key],
    {
        "ubuntu_packages": "content name published on ubuntu."
    })
def check_ubuntu_content(content, all_results):
    """
    Adding data into results.
    """
    all_results[module_dict_key] = content
