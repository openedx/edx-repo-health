#!/usr/bin/env python
"""
This script prints to the console a repository health dashboard derived from SQL queries against the SQLite output
option of a set of repository health data.  It currently consists mainly of:

1) Detected issues which likely require maintenance work to address, in roughly the order that the 2U Platform-Core
   teams would recommend prioritizing them
2) The reasons for each issue being in the list and prioritized as it is
3) The list of repositories impacted by each issue (along with each one's owning/maintaining team)

By default it includes all repositories in the data set, but supports filtering down to just the repositories owned
by one or more specific squads.

The list of recommendations is still very incomplete; the initial choices were chosen either because they have
immediate serious impact or risk, or because they are the long tail of larger projects that were otherwise completed
long ago.
"""
import argparse
import sqlite3
from pathlib import Path

import yaml
from rich.console import Console
from rich.table import Table

DEFAULT_CONFIG_PATH = Path(__file__).parent.parent / "repo_health_dashboard" / "console_dashboard_config.yaml"


def print_table(console: Console, title: str, cursor: sqlite3.Cursor, description: str, aliases: "list[str]") -> None:
    """
    Display a table on the console; omit it if there are no rows to display in it.
    """
    table = Table(title=title, row_styles=["dim", ""])
    for column in cursor.description:
        name = column[0]
        name = aliases.get(name, name)
        table.add_column(name)
    for row in cursor.fetchall():
        table.add_row(*row)
    if table.row_count > 0:
        print("")
        console.print(table)
        console.print(description)


def prepare_query(sql: str, squads: "list[str]") -> str:
    """
    Adjust the provided base SQL query to sort first by squad and then by repo
    name, and to support filtering by squad(s).
    """
    if squads:
        squads_string = "', '".join(squads)
        sql += f" AND ownership_squad IN ('{squads_string}')"
    sql += " ORDER BY ownership_squad, repo_name"
    return sql


def print_dashboard(config_path: str, data_file: str, squads: "list[str]") -> None:
    """
    Print the dashboard defined in this file to the console.
    """
    console = Console()
    conn = sqlite3.connect(data_file)
    with open(config_path, "r") as f:
        config = yaml.safe_load(f)
        print(repr(config))
    tables = config["tables"]
    aliases = config.get("aliases", [])
    for table in tables:
        title = table["title"]
        sql = table["sql"]
        description = table["description"]
        cursor = conn.execute(prepare_query(sql, squads))
        print_table(console, title, cursor, description, aliases)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
                    prog="sql_dashboards",
                    description="Print a set of useful dashboards derived from SQL queries")
    parser.add_argument("sqlite3_file", help="Path to a SQLite file containing the repo health data")
    parser.add_argument("-s", "--squad",
                        help="The space-separated names of one or more owning squads to filter the results to")
    parser.add_argument("-c", "--configuration", default=str(DEFAULT_CONFIG_PATH),
                        help="Path to a YAML file defining the tables to include in the dashboard")
    args = parser.parse_args()
    squad_list = args.squad.split() if args.squad is not None else []
    print_dashboard(args.configuration, args.sqlite3_file, squad_list)
