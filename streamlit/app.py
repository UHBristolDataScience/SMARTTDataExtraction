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


# TODO: move to utilities
def run_query(sql, db=None, server=None, connection_timeout=15, query_timeout=90):

    tc = "yes"
    cnxn = pyodbc.connect(
        'trusted_connection=' + tc
        + ';DRIVER={SQL Server};SERVER=' + server
        + ';DATABASE=' + db
        + ';timeout=%d' % connection_timeout)

    cnxn.timeout = query_timeout
    data = pd.read_sql(sql, cnxn)

    return data


def configure_icca():

    st.header("ICCA Configuration")
    server = st.text_input(
        "Enter SQL Server address:",
        value="ubhnt34.ubht.nhs.uk",
        help="The server on which your research copy of the ICCA database is hosted."
    )
    database = st.text_input(
        "Enter database name:",
        value="CISReportingDB",
        help="The name of your ICCA reporting database."
    )
    test_connection_button = st.button("Test Connection", key="test_con_button")

    if test_connection_button:
        st.session_state.continue_disabled = True
        try:
            test_query = "SELECT TOP 10 * FROM D_Intervention"
            df = run_query(
                test_query, server=server, db=database,
                connection_timeout=2,
                query_timeout=2
            )

            if len(df) > 0:
                st.success("Connection successful!")
                st.session_state.continue_disabled = False
                st.session_state.icca_config = {
                    "server": server,
                    "database": database
                }

        except Exception as e:
            st.error(f"The following exception was caught: {e}")
            st.error("Database connection not successful. Please check ICCA configuration and network settings.")

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

