import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd
from numpy import logical_or
from utilities import (
    _hide_pages, load_interventions,
    get_search_strings_for_variable,
    search_strings_to_logical_index
)

# TODO: log (in schema?) if mapping (and initialisation) is complete for each variable.
# TODO: if (intervention or) attribute have been selected, remove from all subsequent options...(how?)
# TODO: do intervention index reset before saving to sqlite? (currently handled in load_interventions utility mehthod)
# TODO: implement correcting/revising mapping if realise made a mistale.
# TODO: implement copy existing project (with initialisation complete) but create new mapping?


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
        You will now manually map the ICCA database to variables in the project schema by selecting 
        the relevant rows in tables. 
        Please select a schema variable from the dropdown list below, and select all rows in the table that
        correspond to this variable.  
    """
)

incomplete_variables = st.session_state.schema.loc[~st.session_state.schema.mapping_complete].Variable
st.session_state['active_variable'] = st.selectbox(label="Select variable.", options=incomplete_variables)

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
    st.session_state['active_intervention_id'] = int(list(
        st.session_state.selected_interventions.keys()
    )[0])
    st.switch_page("pages/attribute_mapping.py")


