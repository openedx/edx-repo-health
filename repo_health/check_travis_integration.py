"""
Checks repository is on travis.org or .com
"""
import json
import logging
import re

import requests
from pytest_repo_health import add_key_to_metadata

logger = logging.getLogger(__name__)

module_dict_key = "travis_ci"

URL_PATTERN = r"github.com[/:](?P<org_name>[^/]+)/(?P<repo_name>[^/]+).git"


@add_key_to_metadata(module_dict_key)
def check_travis_integration(all_results, git_origin_url):
    """
    Checks repository integrated with travis-ci.org or travis-ci.com
    """

    match = re.search(URL_PATTERN, git_origin_url)
    repo_name = match.group("repo_name")
    
    resp = requests.get(
        url='https://api.travis-ci.org/repo/edx%2F{repo_name}'.format(repo_name=repo_name),
        headers={'Travis-API-Version': '3'}
    )

    if resp.status_code == 200 and json.loads(resp.content)['migration_status'] == 'migrated':
            all_results[module_dict_key]['active_on_com'] = True
            all_results[module_dict_key]['active_on_org'] = False
    else:
        all_results[module_dict_key]['active_on_com'] = False
        all_results[module_dict_key]['active_on_org'] = True
        logger.warning(resp.status_code)
