from unittest.mock import patch

import requests
import responses

from repo_health.check_readme import check_readme_links, module_dict_key


@responses.activate
def test_bad_connection():
    # If you attempt to fetch a url which isn't registered, responses will raise a ConnectionError:
    bad_url = "http://google.com/"
    test_readme = f"{bad_url} is the place to go for more info."
    all_results = {module_dict_key: {}}
    check_readme_links(test_readme, all_results)
    assert "bad_links" in all_results[module_dict_key]
    assert bad_url in all_results[module_dict_key]["bad_links"]
