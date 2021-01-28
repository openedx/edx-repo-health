"""
Check some details in the readme file.
"""

import os.path
import re

from pytest_repo_health import health_metadata

module_dict_key = "readme"

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

BAD_THINGS = {
    "irc-missing": {
        "description": "Has obsolete IRC info",
        "re": [
            r"(?i)`#?edx-code`? IRC channel",
        ],
    },
    "mailing-list-missing": {
        "description": "Has obsolete mailing list info",
        "re": [
            r"https?://groups.google.com/forum/#!forum/edx-code",
        ],
    },
}



@health_metadata(
    [module_dict_key],
    {
        key: val["description"]
        for key, val in {**GOOD_THINGS, **BAD_THINGS}.items()
    }
)
def check_readme_contents(repo_path, all_results):
    """
    Check that the README file has or does not have desired or undesirable contents.
    """
    # This check doesn't care what the readme is called, just that it has the
    # right information in it.  So try a bunch of possibilities.
    for readme_name in ["README.rst", "README.md", "README.txt", "README"]:
        try:
            with open(os.path.join(repo_path, readme_name)) as freadme:
                readme = freadme.read()
            break
        except FileNotFoundError:
            continue
    else:
        # There is no README at all, so nothing to check.
        return

    for key, val in GOOD_THINGS.items():
        present = any(re.search(regex, readme) for regex in val["re"])
        all_results[module_dict_key][key] = present
    for key, val in BAD_THINGS.items():
        present = any(re.search(regex, readme) for regex in val["re"])
        all_results[module_dict_key][key] = not present
