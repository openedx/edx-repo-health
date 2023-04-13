"""
Launch the main data table of a repo health data SQLite file in a web browser.
You'll need to pip install streamlit-aggrid, as it hasn't been added to the
package dependencies yet (and won't be until this experiment is validated a
little further).

Don't run this script directly, instead run:
streamlit run scripts/streamlit_dashboard.py -- path_to_data.sqlite3
"""
import sqlite3
import sys

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

if len(sys.argv) < 2:
    print("Please pass the path to your repo health SQLite data file as an argument")
    sys.exit(1)
data_path = sys.argv[1]
conn = sqlite3.connect(data_path)
df = pd.read_sql("SELECT * FROM dashboard_main", conn)
st.set_page_config(layout="wide")
builder = GridOptionsBuilder.from_dataframe(df)
builder.configure_side_bar()
options = builder.build()
AgGrid(df, gridOptions=options)
