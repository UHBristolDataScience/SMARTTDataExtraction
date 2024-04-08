import streamlit as st
import sqlite3
import json
import pandas as pd
from datetime import datetime
from glob import glob
from pathlib import Path
from utilities import run_query, _hide_pages, LocalDatabaseWrapper

# TODO: change the names of the 'go' continue buttons?

# TODO: add more table types to config.yaml, only using 2 atm (e.g. medications)

# TODO: !!add "with no lock" to ICCA queries in case running on production server.

# TODO: add check that new project name not used already...
# TODO: check if index should be true or False for localdb.enter_df
# TODO: cobine info variables into single dict in session_state
# TODO: remove streamlit-extras from install instructions if not needed anymore (swithc page)

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

# TODO: remove navigation menu?

# TODO: add paths etc to a config file (e.g. schema etc, hidepages...)
# TODO: add sqlite to store intervention and attribute mappings
# TODO: add user accounts? (Mimic auth, with firestore for global mimic mapping)
# TODO: add advanced mode for entering own search strings and bespoke sql queries - where does this happen?
# TODO: add vasopresors/inotropes (other drugs eg effect HR?) And sedation drugs (~5)

# TODO: add ICNARC database linkage section...
# TODO: add user option to input database backup location and create copy (for later use in modelling)

# TODO: consider that unused fact tables at UHBW may store important data at other trusts. Document this.

def setup():
    with open("config.json", 'r') as infile:
        st.session_state["config"] = json.load(infile)

    _hide_pages()


def name_project():

    database_path = Path("../data")
    existing_databases = glob(str(database_path / "*.db"))
    existing_projects = [
        Path(db).stem
        for db in existing_databases
    ]

    st.title("SMARTT Data Federation Toolkit")
    st.write("""
        This software will guide you through 
        the process of harmonizing the data from your clinical information system for use with SMARTT.    
    """)
    st.markdown('<a href="mailto:chris.mcwilliams@bristol.ac.uk">Contact us</a>', unsafe_allow_html=True)
    st.sidebar.markdown('<a href="mailto:chris.mcwilliams@bristol.ac.uk">Contact us</a>', unsafe_allow_html=True)

    selected_project = st.selectbox(
        label="Please either select an existing project to reconnect to:",
        options=existing_projects,
        help="Projects that you created previously should be available to select here.",
        index=None,
        placeholder=""
    )

    project_name = st.text_input(
        "Or enter the name of a new project to create:",
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
        st.session_state["local_db"] = LocalDatabaseWrapper(
            database_path / f"{st.session_state.project_name}.db"
        )
        st.session_state["new_project"] = selected_project is None

        if st.session_state["new_project"]:
            st.session_state["project_creation_datetime"] = (
                datetime.utcnow().strftime('%d-%m-%Y %H:%M:%S')
            )
            st.switch_page("pages/choose_data_source.py")
        else:
            st.switch_page("pages/validate_old_project.py")


if __name__ == "__main__":

    setup()
    name_project()

