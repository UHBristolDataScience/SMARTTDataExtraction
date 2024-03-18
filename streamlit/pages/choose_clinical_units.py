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
    st.session_state.clinical_unit_selection_enabled = True

if st.session_state.get('clinical_unit_selection_enabled', False):
    # TODO: add clinical units, create datetime, last active dattime
    clinical_unit_columns = ['clinicalUnitId', 'displayLabel', 'institution', 'institutionAlternativeId']

    col_string = ", ".join(f"{x}" for x in clinical_unit_columns)
    units = run_query(
        sql=f"SELECT {col_string} FROM D_ClinicalUnit",
        db=st.session_state.icca_config['database'],
        server=st.session_state.icca_config['server']
    ).copy()
    units.insert(0, 'Select', False)

    edited_units = st.data_editor(
        units,
        column_config={
            "Select": st.column_config.CheckboxColumn(
                "Select",
                help="Select which clinical units to use.",
                default=False,
            )
        },
        disabled=clinical_unit_columns,
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
choose_units_button = st.button("Continue", key="choose_units_button")#, disabled=st.session_state.continue_disabled)

if choose_units_button:
    st.session_state['clinical_unit_ids'] = edited_units[edited_units.Select]

    info = {
        "name": [st.session_state.project_name],
        "database_path": [str(Path("../data") / st.session_state.project_name)],
        "schema_file": [st.session_state.schema_file],
        "setup_complete": [False],
        "variable_mapping_progress": [0],
        "source_database": [st.session_state.icca_config["database"]],
        "source_server": [st.session_state.icca_config["server"]],
        "project_creation_datetime": [st.session_state.project_creation_datetime]
    }

    st.session_state.local_db.enter_df(
        df=pd.DataFrame(info),
        name='info',
        index=True
    )
    st.session_state.local_db.enter_df(
        df=pd.DataFrame(st.session_state.clinical_unit_ids),
        name='clinical_unit_ids',
        index=True
    )

    fact_tables = st.session_state.config['icca']['fact_tables']
    ft_status = pd.DataFrame(False, index=fact_tables.keys())
    st.session_state.local_db.enter_df(
        df=ft_status,
        name='fact_table_init_status',
        index=True,
        if_exists='fail'
    )

    st.switch_page("pages/run_initial_sql_queries.py")
