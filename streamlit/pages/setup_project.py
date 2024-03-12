import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd
from pathlib import Path
from utilities import run_query, _hide_pages


# TODO: if project already setup, report details (and progress with mapping)
# TODO: if project not yet setup - get details and run intial SQL queries -: all inte

_hide_pages()

# TODO: define columns in config?
info_columns = {
    "name": st.session_state.project_name,
    "database_path": str(Path("../data") / st.session_state.project_name),
    "schema_file": "smartt_variable_definitions.xlsx",
    "setup_complete": False,
    "variable_mapping_progress": 0,
    "source_database": st.session_state.icca_config["database"],
    "source_server": st.session_state.icca_config["server"]
}

try:
    col_string = ", ".join(f"{x}" for x in info_columns)
    df = pd.read_sql_query(
        f"SELECT {col_string} FROM info",
        st.session_state.local_db_connection
    )
    # for col in info_columns.keys():
    #     st.text_input(label=col, value=df.iloc[0][col], disabled=True)
    st.write("Using project that was setup previously:")
    st.write(info_columns)

except pd.errors.DatabaseError:
    info = {
        col: [
            st.text_input(
                label=col,
                value=info_columns[col]
            )
        ]
        for col in info_columns.keys()
    }

continue_button = st.button("Continue", key="cont_button")#, disabled=st.session_state.continue_disabled)

if continue_button:
    print(pd.DataFrame(info))
    pd.DataFrame(info).to_sql(
        'info',
        st.session_state["local_db_connection"],
        if_exists='replace', index=True
    )

    switch_page("setup_project")
