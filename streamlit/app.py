import streamlit as st
import sqlite3
import json
import pandas as pd
from glob import glob
from pathlib import Path
from streamlit_extras.switch_page_button import switch_page
from utilities import run_query, _hide_pages

# TODO: add local_db_wrapper class to utilities instead of storing connection in session state

# TODO: add clinical unit ID selection to config (query this table).
# TODO: make this app run the intiial SQL queries to build intervention tables.
# TODO:   - then for every intervention that appears in all search_strings in schema
# TODO:   - run sql query to get all attributes in use for that intervention
# TODO:   - display progress as a % of completion (with current action)
# TODO:   - add sqlite3 to dependencies on github
# TODO:   - create sqlite database (let user choose name from list if already exist locally)
# TODO:   - store sql results to database, including progress/completion report for each variable in schema

# TODO:   - step through all interventions, and then through all attributes (live sql query)
# TODO:   - asking user to select relevant attributes and confirm which column contains the data (default valueNumber)
# TODO:   - add progress/completion tracker and instructions
# TODO:   - save attributes in database (attributeIds, labels, columns, units, links to intervention)

# TODO: rrmove navigation menu?

# TODO: add paths etc to a config file (e.g. schema etc, hidepages...)
# TODO: add sqlite to store intervention and attribute mappings
# TODO: add user accounts? (Mimic auth, with firestore for global mimic mapping)
# TODO: add advanced mode for entering own search strings and bespoke sql queries - where does this happen?
# TODO: add vasopresors/inotropes (other drugs eg effect HR?) And sedation drugs (~5)

# TODO: add ICNARC database linkage section...

# TODO: add option to edit schema for prexisting project (and rview project seetings?)

# TODO: add user option to input database backup location and create copy (for later use in modelling)


def setup():
    with open("config.json", 'r') as infile:
        st.session_state['config'] = json.load(infile)

    st.session_state['schema'] = pd.read_excel(
        '../schema/smartt_variable_definitions.xlsx',
        sheet_name='search_strings'
    )
    _hide_pages()


def name_project():

    database_path = Path("../data")
    existing_databases = glob(str(database_path / "*.db"))
    existing_projects = [
        Path(db).stem
        for db in existing_databases
    ]

    st.title("Streamlit App Configuration")

    selected_project = st.selectbox(
        label="Please either select an existing project to reconnect to:",
        options=existing_projects,
        help="Projects that you created previously should be available to select here.",
        index=None,
        placeholder=""
    )

    project_name = st.text_input(
        "Or enter the name of a new project to create::",
        help="""
            Select a name for a new project. It will be used for you to continue your work later if you
            close the app.
            Example: `smartt_data_extraction_april_2024`
        """,
        value=None
    )
    proceed_button = st.button("Proceed", disabled=(project_name is None and selected_project is None))

    if proceed_button:

        st.session_state["project_name"] = selected_project if project_name is None else project_name
        st.session_state["local_db_connection"] = sqlite3.connect(
            database_path / f"{st.session_state.project_name}.db"
        )
        if selected_project is None:
            project_name = selected_project
            st.session_state.schema.to_sql(
                'schema',
                st.session_state["local_db_connection"],
                if_exists='fail', index=False
            )

        switch_page("choose_data_source")


if __name__ == "__main__":
    setup()
    name_project()

