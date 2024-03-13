import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd
from pathlib import Path
from utilities import run_query, _hide_pages


_hide_pages()

st.title("Project Setup")
st.write("""
    The software will now automatically run a few SQL queries to produce an initial extract of your source database.
    This will take some time - **please do not close this window or navigate to another page**.
    You will be notified when the process is complete and you can then proceed with the variable mapping. 
""")

run_init_button = st.button("Go.", key="run_init_button")

if run_init_button:
    # TODO: add clinical units, create datetime, last active dattime


    info = {
        "name": [st.session_state.project_name],
        "database_path": [str(Path("../data") / st.session_state.project_name)],
        "schema_file": [st.session_state.schema_file],
        "setup_complete": [False],
        "variable_mapping_progress": [0],
        "source_database": [st.session_state.icca_config["database"]],
        "source_server": [st.session_state.icca_config["server"]],
        "clinical_unit_ids": st.session_state.clinical_unit_ids
    }

    st.session_state.local_db.enter_df(
        df=pd.DataFrame(info),
        name='info',
        index=True
    )
    # try:
    #     col_string = ", ".join(f"{x}" for x in info_columns)
    #     # df = pd.read_sql_query(
    #     #     f"SELECT {col_string} FROM info",
    #     #     st.session_state.local_db_connection
    #     # )
    #     # for col in info_columns.keys():
    #     #     st.text_input(label=col, value=df.iloc[0][col], disabled=True)
    #     st.write("Using project that was setup previously:")
    #     st.write(info_columns)
    #
    # except pd.errors.DatabaseError:
    #     info = {
    #         col: [
    #             st.text_input(
    #                 label=col,
    #                 value=info_columns[col]
    #             )
    #         ]
    #         for col in info_columns.keys()
    #     }

choose_units_button = st.button("Continue", key="choose_units_button")#, disabled=st.session_state.continue_disabled)

if choose_units_button:
    st.switch_page("pages/intervention_mapping.py")
