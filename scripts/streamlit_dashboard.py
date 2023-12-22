"""
Launch the repo health dashboard in a web browser.

Don't run this script directly, instead run:
streamlit run scripts/streamlit_dashboard.py [path_to_data.sqlite3] [path_to_config.yaml]
"""
import sqlite3
import sys
from pathlib import Path

import pandas as pd
import streamlit as st
import yaml
from st_aggrid import AgGrid, GridOptionsBuilder

REPO_ROOT = Path(__file__).parent.parent
DEFAULT_CONFIG_PATH = REPO_ROOT / "repo_health_dashboard" / "console_dashboard_config.yaml"
DEFAULT_DATA_PATH = REPO_ROOT.parent / "repo-health-data" / "dashboards" / "dashboard.sqlite3"

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


def add_table(title: str, df: pd.DataFrame, description: str, aliases: "list[str]") -> None:
    """
    Add a table to the dashboard; omit it if there are no rows to display in it.
    """
    column_config = {}
    for name in df.columns:
        alias = aliases.get(name, name)
        column_config[name] = alias
    if df.size > 0:
        st.subheader(title)
        st.dataframe(
            df,
            column_config=column_config,
            hide_index=True,
        )
        st.write(description)


# Load the data file
if len(sys.argv) > 1:
    data_path = sys.argv[1]
else:
    data_path = DEFAULT_DATA_PATH
conn = sqlite3.connect(data_path)

# Get the list of known squads
cursor = conn.execute("SELECT DISTINCT(ownership_squad) FROM dashboard_main ORDER BY ownership_squad")
squad_options = [str(row[0]) for row in cursor.fetchall()]

# Configure dashboard-wide settings
st.set_page_config(layout="wide")
cursor = conn.execute("SELECT DISTINCT(TIMESTAMP) FROM dashboard_main ORDER BY TIMESTAMP")
data_date = cursor.fetchall()[0][0]
st.title(f"Repo Health Dashboard (As of {data_date})")
squads = st.multiselect("Squads", squad_options)

# Load the dashboard configuration (prioritized checks and the reasons action is needed)
if len(sys.argv) > 2:
    config_path = sys.argv[2]
else:
    config_path = DEFAULT_CONFIG_PATH
with open(config_path, "r") as f:
    config = yaml.safe_load(f)
tables = config["tables"]
aliases = config.get("aliases", [])

# Add the configured checks to the dashboard
for table in tables:
    title = table["title"]
    sql = table["sql"]
    description = table["description"]
    df = pd.read_sql(prepare_query(sql, squads), conn)
    add_table(title, df, description, aliases)

# Add a raw health check data table, mainly as an aid in updating the dashboard configuration
st.subheader("All Health Data (For Selected Squads)")
st.write("This raw data dump is normally of limited use, but can be very handy when updating the dashboard configuration because it lists all of the column names and value formats in the main data table.")
if squads:
    df = pd.read_sql(f"SELECT * FROM dashboard_main WHERE ownership_squad IN ({','.join('?' for _ in squads)})", conn, params=squads)
else:
    df = pd.read_sql("SELECT * FROM dashboard_main", conn)
builder = GridOptionsBuilder.from_dataframe(df)
builder.configure_side_bar()
options = builder.build()
AgGrid(df, gridOptions=options)
