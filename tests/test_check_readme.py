from unittest.mock import patch

import requests
import responses

from repo_health.check_readme import check_readme_links, module_dict_key


@responses.activate
def test_one_good_one_bad():
    # If you attempt to fetch a url which isn't registered, responses will raise a ConnectionError:
    bad_url = "http://google.com/"
    good_url = "http://rtfd.org"

    responses.add(responses.HEAD, good_url, status=200)
    test_readme = f"{bad_url} is the place to go for more info. {good_url} is better."
    all_results = {module_dict_key: {}}
    check_readme_links(test_readme, all_results)

    assert good_url in all_results[module_dict_key]["good_links"]
    assert any(
        bad.startswith("http://google.com/: Connection refused by Responses")
        for bad in all_results[module_dict_key]["bad_links"]
        )
