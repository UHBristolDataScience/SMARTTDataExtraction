import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd
from datetime import datetime
from numpy import logical_or
from utilities import (
    _hide_pages, load_interventions,
    get_search_strings_for_variable,
    search_strings_to_logical_index,
    full_extraction_query,
    run_query,
    mark_variable_as_mapped
)

# TODO: do intervention index reset before saving to sqlite? (currently handled in load_interventions utility mehthod)
# TODO: implement correcting/revising mapping if realise made a mistake.
# TODO: implement copy existing project (with initialisation complete) but create new mapping?
# TODO: implement cohort selection...

st.set_page_config(layout='wide', initial_sidebar_state='collapsed')


def display_table():
    st.title("ICCA Data Table")
    # Placeholder data (replace with your actual data)
    data = pd.DataFrame({
        "Name": ["Alice", "Bob", "Charlie"],
        "Age": [30, 25, 28]
    })

    # Display the table with checkboxes
    selected_rows = st.dataframe(data, height=200, width=400, editable=True)

    # Confirm selection button
    if st.button("Confirm Selection", help="Click to confirm selected rows"):
        selected_indices = selected_rows.index
        st.write(f"Selected rows: {selected_indices}")

    # Reset data button
    if st.button("Reset Data", help="Reload the original table"):
        display_table()

_hide_pages()

interventions = load_interventions()

st.title("Variable mapping")
st.write(
    """
        You will now manually map the variables in the project schema to their definitions in the ICCA database 
        by selecting the relevant rows in tables. 
        Please select a schema variable from the dropdown list below, and select all rows in the table that
        correspond to this variable.  
    """
)

incomplete_variables = [
    variable
    for variable, completeness in zip(
        st.session_state.schema.Variable,
        st.session_state.schema.mapping_complete
    )
    if not completeness
]

st.session_state['active_variable'] = st.selectbox(label="Select variable.", options=incomplete_variables)


@st.dialog("None selected.")
def confirm_none():
    st.warning(
        """
        You have not selected an intervention. Do you want to skip this variable?
        (If not, please cancel and select from the table.)
        """
    )
    st.write(st.session_state.active_variable)
    st.write(
        st.session_state.local_db.query_pd(
            f"""
                                SELECT * FROM schema
                                WHERE "Variable" = "{st.session_state.active_variable}";
                            """
        )
    )
    if st.button("Yes, skip this variable."):
        mark_variable_as_mapped()
        print("Mapped!")
        st.rerun()


if not st.session_state['active_variable'] is None:
    search_strings = get_search_strings_for_variable(st.session_state['active_variable'])
    logical_index = search_strings_to_logical_index(interventions, search_strings)

    display_cols = ['shortLabel', 'longLabel', 'numberOfPatients', 'firstChartTime', 'lastChartTime']

    these_interventions = interventions[logical_index][display_cols].copy()
    these_interventions.insert(0, 'Select', False)

    edited_df = st.data_editor(
        these_interventions,
        column_config={
            "Select": st.column_config.CheckboxColumn(
                "Select",
                help=f"Select which rows correspond to {st.session_state['active_variable']}.",
                default=False,
            )
        },
        disabled=display_cols,
        hide_index=True,
        num_rows="fixed"
    )

    confirm_button = st.button(
        "Confirm selection",
        key="confirm_intervention_selection"
    )
    if confirm_button:

        st.session_state['selected_interventions'] = {
            interventions.loc[i].interventionId: interventions.loc[i].longLabel
            for i in
            these_interventions.index[edited_df.Select]
        }

        if len(st.session_state['selected_interventions']) == 0:
            confirm_none()

        else:
            st.session_state['active_intervention_id'] = int(list(
                st.session_state.selected_interventions.keys()
            )[0])
            st.switch_page("pages/attribute_mapping.py")

else:
    st.success(
        """
            Congratulations! You have mapped all of the variables in your schema.
            When you are ready, click `Extract` below to produce a full extract
            of the project data.
            This extraction will take a long time.
            Again, you are advised to leave this running overnight and to lock the screen of this computer. 
        """
    )
    extract_button = st.button(
        "Extract."
    )
    if extract_button:
        final_mapping = st.session_state.local_db.query_pd(
            f"""
                SELECT attributeId, tableName
                FROM final_mapping
            """
        )
        for table in pd.unique(final_mapping.tableName):
            st.write(f"Running full extract for table {table}")
            start = datetime.now()
            attribute_list = list(final_mapping[final_mapping.tableName == table].attributeId)
            clinical_units = list(
                st.session_state['clinical_unit_ids'].clinicalUnitId
            )
            for attribute in attribute_list:
                st.write(f"Attribute {attribute} subquery.")
                extract = run_query(
                    full_extraction_query(attribute, table, clinical_units),
                    server=st.session_state.icca_config['server'],
                    db=st.session_state.icca_config['database'],
                    connection_timeout=5,
                    query_timeout=0
                )
                st.session_state.local_db.enter_df(
                    df=extract,
                    name='full_extract',
                    if_exists='append',
                    index=False
                )
            query_time = datetime.now() - start
            st.write(f"Table queries took total {query_time} seconds")
