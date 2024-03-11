import streamlit as st
from streamlit_extras.switch_page_button import switch_page
import pandas as pd
from numpy import logical_or

# TODO: add all tables, not just PtAssess


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


interventions = pd.read_csv('../data/all_ptassessment_interventions_units_5_8_9.rpt', sep='\t')
interventions.dropna(axis=0, subset=['shortLabel', 'longLabel'], inplace=True)

var = st.selectbox(label="Select variable.", options=st.session_state.schema.Variable)

search_strings =[
    s.strip()
    for s in
    st.session_state.schema.loc[
        st.session_state.schema.Variable == var
    ]['Search Strings'].iloc[0].split(',')
]

logical_index = logical_or.reduce(
    [
        interventions.longLabel.str.contains(search_string, case=False)
        for search_string in search_strings
    ]
)

display_cols = ['shortLabel', 'longLabel', 'numberOfPatients', 'firstChartTime', 'lastChartTime']

st.write("Here we map...")

these_interventions = interventions[logical_index][display_cols].copy()
these_interventions.insert(0, 'Select', False)

edited_df = st.data_editor(
    these_interventions,
    column_config={
        "Select": st.column_config.CheckboxColumn(
            "Select",
            help=f"Select which rows correspond to {var}.",
            default=False,
        )
    },
    disabled=display_cols,
    hide_index=True,
    num_rows="fixed"
)

# TODO: implement this:
reset_button = st.button("Reset data")

confirm_button = st.button(
    "Confirm selection",
    key="confirm_intervention_selection"
)
if confirm_button:
    st.session_state['selected_interventions'] = {
        interventions.loc[index].interventionId: interventions.loc[index].longLabel
        for index in
        these_interventions.index[edited_df.Select]
    }
    switch_page("attribute_mapping")


