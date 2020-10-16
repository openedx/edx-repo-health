"""
Checks repository is on travis.org or .com
"""
import json

import requests
from pytest_repo_health import add_key_to_metadata, health_metadata

module_dict_key = "travis_ci"


@add_key_to_metadata(module_dict_key)
def check_travis_integration(all_results, git_origin_url):
    """
    Checks repository integrated with travis-ci.org or travis-ci.com
    """

    # by default assume its not on .com
    all_results[module_dict_key]['active_on_com'] = False
    all_results[module_dict_key]['active_on_org'] = True

    link = git_origin_url.replace('git@github.com:edx/', '').replace('.git', '')  # picking repo name
    resp = requests.get(
        url='https://api.travis-ci.org/repo/edx%2F{link}'.format(link=link),
        headers={'Travis-API-Version': '3'}
    )

    if resp.status_code == 200 and json.loads(resp.content)['migration_status'] == 'migrated':
            all_results[module_dict_key]['active_on_com'] = True
            all_results[module_dict_key]['active_on_org'] = False
