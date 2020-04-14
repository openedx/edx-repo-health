"""
utils used to create dashboard
"""
import csv

def squash_dict(input, delimiter="."):
    """
    Takes very nested dict(dicts inside of dicts) and squashes it to only one level
    For example:
    for input: {'a':{'b':'1', 'c':{'d':'2'}, 'f':[1,2,3]}, 'e':2}
    the output: {'a.f': [1, 2, 3], 'e': 2, 'a.b': '1', 'a.c.d': '2'}
    """
    output = {}
    for key, value in input.items():
        if isinstance(value, dict):
            temp_output = squash_dict(value)
            for key2, value2 in temp_output.items():
                temp_key = key + delimiter + key2
                output[temp_key] = value2
        else:
            output[key] = value
    return output


def get_superset_of_keys(dicts={}):
    """
    Iterates through all the input dicts and returns a superset of keys
    """
    output_set = set()
    for _, item in dicts.items():
        output_set.update(item.keys())
    return output_set


def standardize_dicts(dicts={}):
    """
    Input: dict: squashed dict of one level(no dict nesting)
    Parses through dicts, finds all possible keys(superset) from
    the dicts and makes sure the same keys exist in each dict.
    If a key is missing, it's added with a None value

    TODO(jinder): standardize is not the right name,
    there is a better word for: making all dicts have the same keys
    """
    superset_keys = get_superset_of_keys(dicts)
    output = {}
    for dict_name, item in dicts.items():
        superset_output = {}
        for key in superset_keys:
            if key in item:
                superset_output[key] = item[key]
            else:
                superset_output[key] = None
        output[dict_name] = superset_output
    return output

def squash_and_standardize_dicts(dicts={}):
    """
    Squashes all dicts to only one level and makes sure each has the same keys
    """
    for dict_name, item in dicts.items():
        dicts[dict_name] = squash_dict(item)
    return standardize_dicts(dicts)

def write_squashed_dicts_to_csv(dicts={}, filename="dashboard.csv"):
    """
    Assume all the dicts have the same keys
    """
    superset_keys = list(sorted(get_superset_of_keys(dicts)))
    with open(filename,'w') as csvfile:
        writer = csv.writer(csvfile)
        csv_header = ['repo_name'] + superset_keys
        writer.writerow(csv_header)
        for dict_name, item in dicts.items():
            temp_row = [dict_name]
            for key in superset_keys:
                temp_row.append(item[key])
            writer.writerow(temp_row)
