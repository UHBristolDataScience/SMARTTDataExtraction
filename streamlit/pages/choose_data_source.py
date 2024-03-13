import streamlit as st
from streamlit_extras.switch_page_button import switch_page
from utilities import run_query,_hide_pages


def configure_icca():

    st.write("Please enter the details of your local ICCA reporting database.")
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
        st.session_state.continue_disabled = False

        # st.session_state.continue_disabled = True
        # try:
        #     test_query = "SELECT TOP 10 * FROM D_Intervention"
        #     df = run_query(
        #         test_query, server=server, db=database,
        #         connection_timeout=2,
        #         query_timeout=2
        #     )
        #
        #     if len(df) > 0:
        #         st.success("Connection successful!")
        #         st.session_state.continue_disabled = False
        st.session_state.icca_config = {
            "server": server,
            "database": database
        }
        #
        # except Exception as e:
        #     st.error(f"The following exception was caught: {e}")
        #     st.error("Database connection not successful. Please check ICCA configuration and network settings.")

    continue_button = st.button("Continue", key="cont_button", disabled=st.session_state.continue_disabled)

    if continue_button:
        st.switch_page("pages/choose_schema.py")


_hide_pages()
st.title("Project Setup")
st.write("You will now be guided through the steps to finish setting up your new project.")
st.header("Data source configuration.")
choice = st.selectbox(
    label="Select a data source:",
    options=["MIMIC-IV", "ICCA"],
    index=1,
    help="""
        Select which data source you want to work with.
        (Currently only implemented for a local ICCA reporting server
        running on your network.)  
    """
)

st.session_state.continue_disabled = True

if choice == "ICCA":
    configure_icca()

elif choice == "MIMIC-IV":
    st.markdown(
        """
        **MIMIC-IV Access Information**

        In the future this software will integrate with MIMIC-IV to allow facilitate data extraction from that dataset also. 

        To use the MIMIC-IV dataset, you'll need to follow these steps:

        1. **Apply for Access**: First, apply for access to MIMIC-IV by visiting the MIMIC website and completing the necessary application process.
        2. **Complete Required Training**: Once your access is approved, make sure to complete any required training or certifications.
        3. **Configuration Assistance**: If you already have access or once you've completed the training, contact **chris.mcwilliams@bristol.ac.uk** to configure this application for use with MIMIC-IV.

        Thank you for your interest in MIMIC-IV! 🙌
        """
    )
