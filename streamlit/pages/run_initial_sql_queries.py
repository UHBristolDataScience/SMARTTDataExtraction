import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd
from pathlib import Path
import time
from utilities import (
    run_query, _hide_pages, initial_fact_table_query,
    search_strings_to_logical_index,
    get_search_strings_for_variable
)


_hide_pages()

st.title("Project Setup")
st.write("""
    The software will now automatically run a several long SQL queries to produce an initial extract of your source database.
    This will take some time - **please do not close this window or navigate to another page**.
    Progress is will be displayed below, when the process is complete a success message will be displayed and 
    you can then proceed with the variable mapping. 
""")

run_init_button = st.button("Go.", key="run_init_button")

if run_init_button:
    # TODO: add logic so that query is only run once, then results logged and status logged as complete
    # TODO: add logic to check if setup is complete before coming to this page
    # TODO: change name of choose units button below
    # TODO: deactivate button until all queries completed.
    # TODO: add attribute queries for all search strings in schema...
    # TODO: refactor some of into a class or another file?

    fact_tables = st.session_state.config['icca']['fact_tables']
    clinical_units = list(
        st.session_state['clinical_unit_ids'].clinicalUnitId
    )

    st.write("Running intervention initialisation queries...")
    pc = 0
    intervention_bar = st.progress(0, text="Running query for:")
    pc += 1
    for table, value in fact_tables.items():
        completed = pc / (len(fact_tables) + 1)
        intervention_bar.progress(completed, text=f"Running query for: {table}")

        df = run_query(
            initial_fact_table_query(
                table=table,
                table_type_id=value['tableTypeId'],
                clinical_unit_ids=clinical_units
            ),
            server=st.session_state.icca_config['server'],
            db=st.session_state.icca_config['database'],
            connection_timeout=2,
            query_timeout=900
        )

        st.session_state.local_db.enter_df(
            df=df,
            name=f"{table}Interventions",
            index=True,
            if_exists='fail'
        )
        st.session_state.local_db.insert_query(
            f"""
                UPDATE fact_table_init_status
                SET initialised = True
                WHERE "table_name" = "{table}"; 
            """
        )
        pc += 1

    intervention_bar.progress(1.0, text=f"Running query for: {table}")
    # time.sleep(1)
    # intervention_bar.empty()

    st.write("Running attribute initialisation queries...")
    attribute_bar = st.progress(0, text="Running attribute query for:")

    for vi, variable in enumerate(st.session_state.schema.Variable):
        print(variable)
        completed = vi / len(st.session_state.schema.Variable)
        attribute_bar.progress(completed, text=f"Running attribute query for: {variable}")

        search_strings = get_search_strings_for_variable(variable)
        logical_index = search_strings_to_logical_index(df, search_strings)
        these_interventions = df[logical_index]

        for intervention_id in these_interventions.interventionId:
            attribute_bar.progress(completed, text=f"Running attribute query for: {variable} (interventionId: {intervention_id})")
            time.sleep(1)

    attribute_bar.progress(1.0, text=f"Running attribute query for: {ai}")

    st.session_state.local_db.insert_query(
        f"""
            UPDATE info
            SET setup_complete = True
            WHERE "name" = "{st.session_state.project_name}";
        """
    )

    st.success(f"""
        Initialisation queries complete! You may now continue to the variable mapping, or close this 
        page and return to the project later by selecting `{st.session_state.project_name}` from the 
        dropdown menu when you first open the application. 
    """)

choose_units_button = st.button("Continue", key="choose_units_button")#, disabled=st.session_state.continue_disabled)

if choose_units_button:
    st.switch_page("pages/intervention_mapping.py")
