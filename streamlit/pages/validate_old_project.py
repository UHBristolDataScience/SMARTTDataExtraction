import streamlit as st
import pandas as pd
from utilities import run_query, _hide_pages


_hide_pages()

st.title("Project Setup")
st.write("""
    You have chosen to use an existing project. Please validate this 
    project to check that everything was setup correctly last time.
""")
validate_button = st.button(
    "Validate project.", key="setup_button",
)
st.session_state["pending_validation"] = True

if validate_button:

    info_columns = dict.fromkeys(
        st.session_state["config"]["project"]["info_columns"],
        None
    )

    try:
        col_string = ", ".join(f"{x}" for x in info_columns)
        df = st.session_state.local_db.query_pd(f"SELECT {col_string} FROM info")

        st.write("Using project that was setup previously:")
        st.write(df.to_dict(orient='records')[0])
        st.session_state.icca_config = {
            "server": df.iloc[0]['source_server'],
            "database": df.iloc[0]['source_database']
        }
        df = st.session_state['clinical_unit_ids'] = st.session_state.local_db.query_pd(
            "SELECT * FROM clinical_unit_ids"
        )
        st.write("This project uses the following clinical units:")
        st.write(df[['clinicalUnitid', 'displaylabel', 'institution']])
        st.session_state['schema'] = st.session_state.local_db.query_pd("SELECT * FROM schema")
        st.session_state["pending_validation"] = False

    except pd.errors.DatabaseError as e:
        st.error(f"The following exception was caught: {e}")
        st.error("Cannot access local database entry for your project. Please check project name.")
        st.warning("""
            If you previously did not finish setting up this project, please start again 
            by selecting the `home` page in the navigation menu and naming a new project.
        """)

to_mapping_button = st.button("Continue", disabled=st.session_state.pending_validation)

if to_mapping_button:
    st.switch_page("pages/intervention_mapping.py")
