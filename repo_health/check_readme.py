"""
Check some details in the readme file.
"""

import os.path
import re
import urllib.parse

import pytest
import requests

from pytest_repo_health import health_metadata

module_dict_key = "readme"

# Good things should be there, and are True if they are present.
GOOD_THINGS = {
    "security": {
        "description": "Has a security contact",
        "re": [
            r"security@edx\.org",
        ],
    },
    "getting-help": {
        "description": "Has a link to get help",
        "re": [
            r"https://open\.?edx\.org/getting-help",
        ],
    },
}

# Bad things should not be there, and are True if they are absent, so that all
# the values should be True.
BAD_THINGS = {
    "irc-missing": {
        "description": "Avoids obsolete IRC info",
        "re": [
            r"(?i)`#?edx-code`? IRC channel",
        ],
    },
    "mailing-list-missing": {
        "description": "Avoids obsolete mailing list info",
        "re": [
            r"https?://groups.google.com/forum/#!forum/edx-code",
        ],
    },
}


@pytest.fixture(name='readme')
def fixture_readme(repo_path):
    """Fixture producing the text of the readme file."""
    # These checks don't care what the readme is called, just that it has the
    # right information in it.  So try a bunch of possibilities.
    for readme_name in ["README.rst", "README.md", "README.txt", "README"]:
        try:
            with open(os.path.join(repo_path, readme_name), encoding="utf-8") as freadme:
                return freadme.read()
        except FileNotFoundError:
            continue

    # There is no README at all, so nothing to check.
    return None



@health_metadata(
    [module_dict_key],
    {
        key: val["description"]
        for key, val in {**GOOD_THINGS, **BAD_THINGS}.items()
    }
)
def check_readme_contents(readme, all_results):
    """
    Check that the README file has or does not have desired or undesirable contents.
    """
    if readme is None:
        return

    for key, val in GOOD_THINGS.items():
        present = any(re.search(regex, readme) for regex in val["re"])
        all_results[module_dict_key][key] = present
    for key, val in BAD_THINGS.items():
        present = any(re.search(regex, readme) for regex in val["re"])
        all_results[module_dict_key][key] = not present


URL_REGEX = r"https?://[\w._/?&%=@+\-\[\]]+"

# Some links in READMEs are just examples, don't bother checking these domains.
EXAMPLE_DOMAINS = {
    "localhost",
    "127.0.0.1",
    "example.com",
    ".ngrok.io",
}

# If a URL has any weird meta-characters, it's not a real URL.
METACHARACTERS = r"[\[\]]"

def is_example_url(url):
    """
    Is this URL just an example, no need to check it?
    """
    if re.search(METACHARACTERS, url):
        return True
    parts = urllib.parse.urlparse(url)
    for domain in EXAMPLE_DOMAINS:
        if domain == parts.hostname:
            return True
        if domain.startswith(".") and parts.hostname.endswith(domain):
            return True
    return False

@health_metadata(
    [module_dict_key],
    {
        "bad_links": "Links in the README that can't be fetched.",
        "good_links": "Links in the README that are good.",
    }
)
def check_readme_links(readme, all_results):
    """
    Check that the links in the README actually work.
    """
    return
    if readme is None:
        return

    seen = set()
    bad = all_results[module_dict_key]["bad_links"] = []
    good = all_results[module_dict_key]["good_links"] = []

    for url in re.findall(URL_REGEX, readme):
        if url in seen:
            continue
        seen.add(url)
        if is_example_url(url):
            continue
        try:
            resp = requests.head(url, allow_redirects=True)
        except requests.ConnectionError as e:
            bad.append(f"{url}: {e}")
            continue

        if 200 <= resp.status_code <= 300:
            good.append(url)
        else:
            bad.append(f"{url}: {resp.status_code}")
