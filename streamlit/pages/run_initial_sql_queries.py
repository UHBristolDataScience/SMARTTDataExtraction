import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd
from pathlib import Path
from utilities import run_query, _hide_pages, initial_fact_table_query


_hide_pages()

st.title("Project Setup")
st.write("""
    The software will now automatically run a few SQL queries to produce an initial extract of your source database.
    This will take some time - **please do not close this window or navigate to another page**.
    You will be notified when the process is complete and you can then proceed with the variable mapping. 
""")

run_init_button = st.button("Go.", key="run_init_button")

if run_init_button:
    # TODO: move all this to final if clause in choose_clinical_units (and just handle sql queries here)
    # TODO: change name of choose units button below
    st.warning("Running initial queries - this may take a while...")

    df = run_query(
        initial_fact_table_query(),
        server=st.session_state.icca_config['server'],
        db=st.session_state.icca_config['database'],
        connection_timeout=2,
        query_timeout=360
    )
    st.warning("Running query: PtAssessment...")
    print(df.head())
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
