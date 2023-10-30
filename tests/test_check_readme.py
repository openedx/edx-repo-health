"""Test checks of README."""

import re

import responses

from repo_health.check_readme import check_readme_links, module_dict_key


@responses.activate
def test_one_good_one_bad():
    # If you attempt to fetch a url which isn't registered, responses will raise a ConnectionError:
    bad_url = "http://badurl.com/"
    good_url = "http://goodurl.org"

    # Any url at good_url will be OK.
    good_match = re.compile(f"{good_url}(/.*)?")
    responses.add(responses.HEAD, good_match, status=200)

    test_readme = f"""
        {bad_url} is the place to go for more info.
        {good_url} is better.
        End of a sentence is ok: {good_url}.
        Commas are fine: {good_url}, {bad_url}.
        In parens is ok: ({good_url}).
        {good_url}/page?x=1&y=2 is also a URL,
        and {good_url}/page/another/ will be fine.
        """
    all_results = {module_dict_key: {}}
    check_readme_links(test_readme, all_results)

    assert good_url in all_results[module_dict_key]["good_links"]

    bad_links = all_results[module_dict_key]["bad_links"]
    print(bad_links)
    assert len(bad_links) == 1
    assert bad_links[0].startswith(f"{bad_url}: Connection refused by Responses")
