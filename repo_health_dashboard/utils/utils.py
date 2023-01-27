"""
utils used to create dashboard
"""
import csv
import html
import os
import re
import sqlite3


def squash_dict(input_dict, delimiter="."):
    """
    Takes very nested dict(metadata_by_repo inside of metadata_by_repo) and squashes it to only one level
    For example:
    for input: {'a':{'b':'1', 'c':{'d':'2'}, 'f':[1,2,3]}, 'e':2}
    the output: {'a.f': [1, 2, 3], 'e': 2, 'a.b': '1', 'a.c.d': '2'}
    """
    output = {}
    for key, value in input_dict.items():
        if isinstance(value, dict):
            temp_output = squash_dict(value)
            for key2, value2 in temp_output.items():
                temp_key = key + delimiter + key2
                output[temp_key] = value2
        else:
            output[key] = value
    return output


def get_superset_of_keys(dicts):
    """
    Iterates through all the input dicts and returns a superset of keys
    """
    output_set = set()
    for _, item in dicts.items():
        output_set.update(item.keys())
    return output_set


def standardize_metadata_by_repo(metadata_by_repo):
    """
    Input: dict: squashed dict of one level(no dict nesting)
    Parses through metadata_by_repo dict, finds all possible keys(superset) from
    the metadata_by_repo and makes sure the same keys exist in each dict.
    If a key is missing, it's added with a None value

    TODO(jinder): standardize is not the right name,
    there is a better word for: making all metadata_by_repo have the same keys
    """
    superset_keys = get_superset_of_keys(metadata_by_repo)
    defaults = {k: None for k in superset_keys}
    output = {}
    for dict_name, item in metadata_by_repo.items():
        superset_output = defaults.copy()
        superset_output.update(item)
        output[dict_name] = superset_output
    return output


def squash_and_standardize_metadata_by_repo(metadata_by_repo):
    """
    Squashes all metadata_by_repo to only one level and makes sure each has the same keys
    """
    for dict_name, item in metadata_by_repo.items():
        metadata_by_repo[dict_name] = squash_dict(item)
    return standardize_metadata_by_repo(metadata_by_repo)


def get_sheets(parsed_yaml_file, sheet_name):
    """
    Parses configuration yaml file and makes sure each requested output configuration has
    the right setting keys

    Rest of the system expects the keys("check_order", "repo_name_order", and "key_aliases")
    to exists in configuration dict
    """
    sheet_configuration = {}
    sheet_configuration.update(parsed_yaml_file[sheet_name])
    sheet_configuration["check_order"] = parsed_yaml_file[sheet_name].get(
        "check_order", []
    )
    sheet_configuration["repo_name_order"] = parsed_yaml_file[sheet_name].get(
        "repo_name_order", []
    )
    sheet_configuration["key_aliases"] = parsed_yaml_file[sheet_name].get(
        "key_aliases", {}
    )
    return sheet_configuration


def get_sorted_keys(metadata_by_repo, configuration):
    """
    Return a list of keys for the metadata_by_repo, sorted by the check_order
    """
    # Get a superset of all keys in the metadata_by_repo dictionaries
    superset_keys = get_superset_of_keys(metadata_by_repo)

    # Discard keys that are not in the configuration check order
    for key in configuration["check_order"]:
        superset_keys.discard(key)

    # Determine the sorted keys to use based on the configuration
    if configuration.get("subset", False):
        sorted_keys = configuration["check_order"]
    else:
        sorted_keys = configuration["check_order"] + list(sorted(superset_keys))

    return sorted_keys


def get_sorted_aliased_keys(metadata_by_repo, configuration):
    """
    Return a list of aliased keys for the metadata_by_repo, sorted by the check_order
    """
    sorted_keys = get_sorted_keys(metadata_by_repo, configuration)

    # Change key names to their aliases for display
    sorted_aliased_keys = []
    for key in sorted_keys:
        if key in configuration["key_aliases"]:
            sorted_aliased_keys.append(configuration["key_aliases"][key])
        else:
            sorted_aliased_keys.append(key)

    return sorted_aliased_keys


def write_squashed_metadata_to_csv(metadata_by_repo, filename, configuration, append):
    """
    Assume all the metadata_by_repo have the same keys
    """
    sorted_keys = get_sorted_keys(metadata_by_repo, configuration)

    # change key names to its alias for display(csv header row)
    sorted_aliased_keys = get_sorted_aliased_keys(metadata_by_repo, configuration)

    mode = 'a' if append else 'w'
    with open(filename + ".csv", mode, encoding="utf8") as csvfile:
        writer = csv.writer(csvfile)
        # In case of appending an empty file, we still need headers
        if not append or os.path.getsize(filename + ".csv") == 0:
            csv_header = ["repo_name"] + sorted_aliased_keys
            writer.writerow(csv_header)

        # TODO(jinder): order repos based on configuration["repo_name_order"]
        for repo_name, item in metadata_by_repo.items():
            writer.writerow(
                [repo_name] + [item[k] if k in item else None for k in sorted_keys]
            )


def write_squashed_metadata_to_html(metadata_by_repo=None, filename="dashboard.html"):
    """
    Write HTML report of repo metadata (takes output of squash-and-standardize).
    """
    if not metadata_by_repo:
        metadata_by_repo = {}
    sorted_key_tuples = sorted(list(get_superset_of_keys(metadata_by_repo)))

    with open(filename + ".html", "w", encoding="utf8") as f:
        f.write(
            """<!DOCTYPE html>
<html lang="en">
<head>
  <title>Repo health dashboard</title>
  <style>
    table {
        border-collapse: collapse;
        border: 2px solid rgb(100, 100, 100);
        font-family: sans-serif;
    }

    td, th {
        border: 1px solid rgb(100, 100, 100);
        padding: .5rem .5rem;
    }

    td {
        text-align: center;
    }

    caption {
        padding: .5rem;
        caption-side: top;
        text-align: start;
    }
  </style>
</head>
<body>\n"""
        )
        f.write("""<table>\n""")
        f.write(
            "<caption>Results of health checks for various repositories</caption>\n"
        )

        f.write("<thead>\n")
        f.write("""  <tr>\n""")
        f.write("""    <th scope="col">Repository</th>\n""")
        for k in sorted_key_tuples:
            f.write(f"""    <th scope="col">{html.escape(k)}</th>\n""")
        f.write("  </tr>\n")
        f.write("</thead>\n")

        f.write("<tbody>\n")
        # TODO(timmc): Sort rows by repo name
        for dict_name, item in metadata_by_repo.items():
            f.write("  <tr>\n")
            f.write(f"""    <th scope="row">{html.escape(dict_name)}</th>\n""")
            for k in sorted_key_tuples:
                f.write(f"""    <td><pre>{html.escape(str(item[k]))}</pre></td>\n""")
            f.write("  </tr>\n")
        f.write("</tbody>\n")
        f.write("</table>\n")
        f.write("</body></html>\n")


def write_squashed_metadata_to_sqlite(metadata_by_repo, table_name, configuration, sqlite_output):
    """
    Assume all the metadata_by_repo have the same keys
    """
    # Get a superset of all keys in the metadata_by_repo dictionaries
    sorted_keys = get_sorted_keys(metadata_by_repo, configuration)

    # Change key names to their aliases for display
    sorted_aliased_keys = get_sorted_aliased_keys(metadata_by_repo, configuration)

    # Connect to the SQLite database file
    conn = sqlite3.connect(f"{sqlite_output}.sqlite3")
    c = conn.cursor()

    columns = ["repo_name"] + sorted_aliased_keys

    # Replace '.', '-', ':' with _ in the column names because sqlite doesn't accept those tokens in column names
    columns = [re.sub(r"[\.\-\:]", "_", column) for column in columns]
    sqlite_columns = []
    # Get first row of the data and infer types of the columns from it
    repo_name, item = next(iter(metadata_by_repo.items()))
    data_column = [repo_name] + [item[k] if k in item else None for k in sorted_keys]

    for index, value in enumerate(data_column):
        if isinstance(value, int):
            sqlite_columns.append(f'{columns[index]} integer')
        elif isinstance(value, float):
            sqlite_columns.append(f'{columns[index]} real')
        elif isinstance(value, bool):
            sqlite_columns.append(f'{columns[index]} boolean')
        else:
            sqlite_columns.append(f'{columns[index]} text')

    query = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(sqlite_columns)})"
    c.execute(query)

    # Iterate through the data and insert in database
    for repo_name, item in metadata_by_repo.items():
        values = [repo_name] + [str(item[k]) if not isinstance(item[k], (int, float, bool))
                                else item[k] if k in item else None for k in sorted_keys]
        c.execute(f'''INSERT INTO {table_name} VALUES (?, {', '.join(['?' for key in sorted_keys])})''',
                  values)

    # Save the changes to the database and close the connection
    conn.commit()
    with open(sqlite_output + '.sql', 'w') as f:
        for line in conn.iterdump():
            f.write('%s\n' % line)
    conn.close()
