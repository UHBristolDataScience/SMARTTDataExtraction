import streamlit as st
import sqlite3
import json
import pandas as pd
from datetime import datetime
from glob import glob
from pathlib import Path
from utilities import run_query, _hide_pages, LocalDatabaseWrapper

# TODO: check index columns for all tables in schema (try using partial index?) and add indexing to initial sql queries (add to instructions).
# TODO: add PtDemographic (and other?) table. Add DOB, ethnic group, postcode, admit source/source of admission, hospital number...
# TODO: handle row duplication/intervention done twice - see run_initial_sql_wuereis...
# TODO: BMI -> weight + height
# TODO: handle variables with no interventions, or no attributes/example data (e.g. BM)
# TODO: handle free form lab result - try casting valueString to numeric for median
# TODO: button to view multiple samples for a select attribute
# TODO: add frequency column to attribute table
# TODO: make attribute table display in wide mode without sidebar

# TODO: add warning that full extract will take time! (and better progress bar)

# TODO: change the names of the 'go' continue buttons?
# TODO: remove/deactivate 'continue' when 'go' should be selected (e.g. when setting up a new project)

# TODO: add more table types to config.yaml, only using 2 atm (e.g. medications)

# TODO: !!add "with no lock" to ICCA queries in case running on production server.

# TODO: add check that new project name not used already...
# TODO: check if index should be true or False for localdb.enter_df
# TODO: combine info variables into single dict in session_state
# TODO: remove streamlit-extras from install instructions if not needed anymore (switch page)

# TODO: add clinical unit ID selection to config (query this table).

# TODO:   - save attributes in database (attributeIds, labels, columns, units, links to intervention)

# TODO: remove navigation menu?

# TODO: add paths etc to a config file (e.g. schema etc, hidepages...)

# TODO: add vasopresors/inotropes (other drugs eg effect HR?) And sedation drugs (~5)

# ***************************************************************************************
# TODO FUTURE:
# TODO: migrate to SQLAlchemy (for pandas sql usage)
# TODO: add 'back' or 'edit' functionality to both intervention and attribute mapping
# TODO: Currently assuming all data is numeric. Add select is_string option to attribute_mapping? (other data columns?)
# TODO: Add prioritisation option? Currently this will be handled automatically.
# TODO: consider that unused fact tables at UHBW may store important data at other trusts. Document this.
# TODO: add ICNARC database linkage section...
# TODO: implement saving comments (on attribute_mapping page)
# TODO: implement refresh data to get a new sample of example attribute data (pass new random state to load method)
#     note: this will clear existing selections. (on attribute_mapping page)
# TODO: After completing all attributes and interventions, present coverage report. Does all seem OK? If not...log.
# TODO: Handle selection of intervention with no example data? (on attribute_mapping page)(shouldn't happen in theory.)
# TODO: add user accounts? (Mimic auth, with firestore for global mimic mapping)
# TODO: add advanced mode for entering own search strings and bespoke sql queries - where does this happen?
# TODO: add user option to input database backup location and create copy (for later use in modelling)
# TODO: add option to inspect more than one sample, for sanity checking of values (on attribute_mapping page)
# TODO: add option to select maybe/need more info (on attribute_mapping page)
# TODO: show number of patients (on attribute_mapping page) (i.e. is it a niche or test attribute? - could explain weird values)
# TODO: add capability to do extract for specific cohort of patients/icu stays

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

    st.title("The Sniffer")
    st.write("""
        This software is called 'The Sniffer' in honour of Dr Gould who first conceived of it many years ago.
        It is designed to help you sniff out the data that you require for your research or service evaluation
        project, from the messy backend of your clinical information system. 
        
        You will be guided through 
        the process of setting up and using this tool and can view additional guidance by hovering over the ? 
        symbol, where available. If you encounter any issues, please get in touch via email. There is a contact link 
        below and in the navigation menu. 
        
        Happy sniffing! 
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

