import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd
from glob import glob
from pathlib import Path
from utilities import run_query, _hide_pages


_hide_pages()

st.title("Project Setup")
st.write("You will now be guided through the steps to finish setting up your new project.")

schema_path = Path("../schema")
existing_schemas = glob(str(schema_path / "*.xlsx"))
existing_schemas = [
    Path(sch).name
    for sch in existing_schemas
]

schema_file = st.selectbox(
        label="Enter a schema file for this project:",
        options=existing_schemas,
        help="""
            This is an excel file that defines the variables that you want to extract,
            and the search strings that will be used to help you locate these variables
            in the database. 
        """,
        index=None,
        placeholder=""
    )

if 'select_schema_button' not in st.session_state:
    st.session_state['select_schema_disabled'] = True

st.session_state['select_schema_disabled'] = (schema_file is None or schema_file == '')

select_schema_button = st.button(
    "Continue",
    key="select_schema_button",
    disabled=st.session_state.select_schema_disabled
)

if select_schema_button:
    try:
        st.session_state['schema_file'] = schema_file
        st.session_state['schema'] = pd.read_excel(
            f"../schema/{schema_file}",
            sheet_name='search_strings'
        )
        st.session_state['schema'].insert(0, "mapping_complete", False)
        st.session_state.local_db.enter_df(
            st.session_state.schema,
            name='schema'
        )
        st.switch_page("pages/choose_clinical_units.py")

    except FileNotFoundError:
        st.error("""
            Could not find that schema file. Please check you have entered the name
            of a correct .xlsx file that is present in the `schema/` directory.
        """)

