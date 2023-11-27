# pylint: disable=django-not-configured

"""
This package contains checks for edx/openedx dependencies
"""

import shutil
import requests

import pytest
import csv

__version__ = "1.0.0"


# GitHub raw URL for the file
GITHUB_RAW_URL = "https://github.com/zubairshakoorarbisoft/pypi-dependencies-updates/blob/zshkoor/dev/dependencies_urls.csv"
DEPENDENCIES_URL_FILE_NAME="dependencies_urls.csv"
GITHUB_ACCESS_TOKEN = "GITHUB_ACCESS_TOKEN"


def download_file(url, local_filename, token):
    headers = {'Authorization': f'token {token}'}
    try:
        with requests.get(url, headers=headers, stream=True) as response:
            response.raise_for_status()
            with open(local_filename, 'wb') as file:
                response.raw.decode_content = True
                shutil.copyfileobj(response.raw, file)
    except requests.RequestException as e:
        print(f"Failed to download file from {url}. Exception: {e}")


def get_dependencies(dependencies_url_file_path):
    dependency_urls_list = []

    with open(dependencies_url_file_path, 'r') as file:
        csv_reader = csv.reader(file)

        # Skip the timestamp row
        next(csv_reader, None)

        # Use the second row as the header
        header = next(csv_reader, None)

        for row in csv_reader:
            # Create a dictionary using the header and row
            row_dict = dict(zip(header, row))
            dependency_urls_list.append(
                {
                    "dependency": row_dict.get('dependency'),
                    "source": row_dict.get('source')
                }
            )

    return dependency_urls_list


@pytest.fixture(name='dependency_urls')
def fixture_dependency_urls():
    download_file(
        GITHUB_RAW_URL,
        DEPENDENCIES_URL_FILE_NAME,
        GITHUB_ACCESS_TOKEN
    )
    """Fixture producing the dependencies list
       from dependencies_urls.csv.
    """
    return get_dependencies(
        DEPENDENCIES_URL_FILE_NAME
    )
