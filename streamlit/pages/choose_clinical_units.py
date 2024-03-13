import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd
from pathlib import Path
from utilities import run_query, _hide_pages


_hide_pages()

st.title("Project Setup")
st.write("You will now be guided through the steps to finish setting up your new project.")
setup_button = st.button("Go.", key="setup_button")

if setup_button:
    # TODO: add clinical units, create datetime, last active dattime

    units = run_query(
        sql="SELECT clinicalUnitId, displayLabel, institution, institutionAlternativeId FROM D_ClinicalUnit",
        db=st.session_state.icca_config['database'],
        server=st.session_state.icca_config['server']
    ).copy()
    static_cols = units.columns
    units.insert(0, 'Select', False)

    edited_df = st.data_editor(
        units,
        column_config={
            "Select": st.column_config.CheckboxColumn(
                "Select",
                help=f"Select which clinical units to use.",
                default=False,
            )
        },
        disabled=static_cols,
        hide_index=True,
        num_rows="fixed"
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
#
# choose_units_button = st.button("Continue", key="choose_units_button")#, disabled=st.session_state.continue_disabled)
#
# if choose_units_button:
#     print(pd.DataFrame(info))
#     pd.DataFrame(info).to_sql(
#         'info',
#         st.session_state["local_db_connection"],
#         if_exists='fail', index=True
#     )
#
#     switch_page("pages/run_initial_sql_queries.py")
