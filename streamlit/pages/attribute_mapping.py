import streamlit as st
import time
from utilities import _hide_pages, load_example_data

# TODO: ask user to also select data column? e.g. checkbox column "IsString"
# TODO: implement refresh data to get a new sample of example attribute data (pass new random satte to load method)
#     note: this will clear existing selections.

_hide_pages()
st.write(
    f"""
        You selected the following {len(st.session_state.selected_interventions)} interventions
        for the variables {st.session_state['active_variable']}: 
        {st.session_state.selected_interventions}
    """
)
st.write(
    """
        Please select, in the table below, the rows corresponding to the attributes that contain the 
        relevant data for this intervention. Once you are happy with your selection, please proceed 
        to the next intervention using the button below.
    """
)

next_button = st.button("Next intervention")

if next_button:
    temp = list(st.session_state.selected_interventions)
    try:
        st.session_state['active_intervention_id'] = temp[temp.index(st.session_state.active_intervention_id) + 1]

    except (ValueError, IndexError):
        st.session_state['active_intervention_id'] = None
        st.success(
            """
            You have mapped all interventions for this variable!
            You will now return to select another variable to map...
            """
        )
        time.sleep(2)
        st.switch_page("pages/intervention_mapping.py")
        # TODO: store selected attributes to new table: called e.g. "final_mapping"
        # TODO: return to variable mapping and do a different variable! (remove done from list)

st.write(
    f"""
        Currently mapping attributes for intervention: {
            st.session_state.selected_interventions[st.session_state.active_intervention_id]
        } (ID: {st.session_state.active_intervention_id}).
    """
)
attribute_id_list = st.session_state.local_db.query_pd(
    f"""
        SELECT *
        FROM distinct_attributes
        WHERE interventionId="{st.session_state['active_intervention_id']}" 
    """
)
print("LIST HERE: ", attribute_id_list)
df = load_example_data(attribute_id_list)

# disabled_columns = ['shortLabel', 'verboseForm', 'valueNumber', 'valueString']
display_columns = ['shortLabel', 'valueNumber', 'valueString', 'unitOfMeasure']

attribute_df = df[display_columns].copy()
attribute_df.insert(0, 'Select', False)
print(attribute_df.head())
edited_attribute_df = st.data_editor(
    attribute_df,
    column_config={
        "Select": st.column_config.CheckboxColumn(
            "Select",
            help=f"Select which contain the data for {st.session_state['active_variable']}.",
            default=False,
        )
    },
    disabled=display_columns,
    hide_index=True,
    num_rows="fixed"
)
# TODO: after select, click next to save current selection and step to next intervention
st.text_input(
    label="If you have any comments of observations, please enter them here."
)
# st.write("We now step through each, and ask the user to select attributes. Also allows comments if something not right")
# TODO: After completing all attributes and interventions, present coverage report. Does all seem OK? If not...log.
