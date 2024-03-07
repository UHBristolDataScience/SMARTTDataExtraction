import streamlit as st
import pyodbc
import pandas as pd
from streamlit_extras.switch_page_button import switch_page
from st_pages import hide_pages

# TODO: add clinical ID selection to config (query this table).
# TODO: make this app run the intiial SQL queries to build intervention tables?
# TODO: add paths etc to a config file (e.g. schema etc)
# TODO: add sqlite to store intervention and attribute mappings
# TODO: add user accounts?


def setup():
    st.session_state['schema'] = pd.read_excel(
        '../schema/smartt_variable_definitions.xlsx',
        sheet_name='search_strings'
    )
    hide_pages(
        ['intervention_mapping', 'attribute_mapping']
    )


def homepage():

    st.title("Streamlit App Configuration")
    choice = st.selectbox("Select an option:", ["MIMIC-IV", "ICCA"])

    st.session_state.continue_disabled = True

    if choice == "ICCA":
        configure_icca()

    elif choice == "MIMIC-IV":
        st.markdown(
            """
            **MIMIC-IV Access Information**

            To use the MIMIC-IV dataset, you'll need to follow these steps:

            1. **Apply for Access**: First, apply for access to MIMIC-IV by visiting the MIMIC website and completing the necessary application process.
            2. **Complete Required Training**: Once your access is approved, make sure to complete any required training or certifications.
            3. **Configuration Assistance**: If you already have access or once you've completed the training, contact **chris.mcwilliams@bristol.ac.uk** to configure this application for use with MIMIC-IV.

            Thank you for your interest in MIMIC-IV! 🙌
            """
        )


def configure_icca():

    st.header("ICCA Configuration")
    server = st.text_input("Enter SQL Server address:")
    database = st.text_input("Enter database name:")
    test_connection_button = st.button("Test Connection", key="test_con_button")

    if test_connection_button:
        st.session_state.continue_disabled = True
        # try:
        #     # Attempt to connect to the SQL server
        #     conn = pyodbc.connect(f"DRIVER={{SQL Server}};SERVER={server};DATABASE={database}")
        st.success("Connection successful!")
        st.session_state.continue_disabled = False

    continue_button = st.button("Continue", key="cont_button", disabled=st.session_state.continue_disabled)

    if continue_button:
        print("change..")
        switch_page("intervention_mapping")

        #         st.write("Continue to the next page...")
        # except pyodbc.Error as e:
        #     st.error(f"Connection failed: {e}. Please check configuration.")
        # return True


if __name__ == "__main__":
    setup()
    homepage()

