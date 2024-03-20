import streamlit as st
from utilities import _hide_pages, load_example_data

# TODO: ask user to also select data column?

_hide_pages()
st.write(f"Selected interventions: {st.session_state.selected_interventions}")

next_button = st.button("Next")

if next_button:
    temp = list(st.session_state.selected_interventions)
    try:
        st.session_state['active_intervention_id'] = temp[temp.index(st.session_state.active_intervention_id) + 1]

    except (ValueError, IndexError):
        st.session_state['active_intervention_id'] = None
        st.success("You have mapped all interventions for this variable!")
        # TODO: return to variable mapping and do a different variable! (remove done from list)

st.write(
    f"""
        Active intervention: {
            st.session_state.selected_interventions[st.session_state.active_intervention_id]
        } (ID: {st.session_state.active_intervention_id}).
    """
)
attribute_id_list = st.session_state.local_db.query_pd(
    f"""
        SELECT attributeId
        FROM distinct_attributes
        WHERE interventionId="{st.session_state['active_intervention_id']}" 
    """
)
df = load_example_data(attribute_id_list)

df.insert(0, 'Select', False)

# disabled_columns = ['shortLabel', 'verboseForm', 'valueNumber', 'valueString']
disabled_columns = ['shortLabel', 'valueNumber', 'valueString', 'unitOfMeasure']
display_columns = ['Select'] + disabled_columns
edited_df = st.data_editor(
    df[display_columns],
    column_config={
        "Select": st.column_config.CheckboxColumn(
            "Select",
            help=f"Select which contain the data for {st.session_state['active_variable']}.",
            default=False,
        )
    },
    disabled=disabled_columns,
    hide_index=True,
    num_rows="fixed"
)
# TODO: after select, click next to save current selection and step to next intervention

st.write("We now step through each, and ask the user to select attributes. Also allows comments if something not right")
st.write("After completing all attributes and interventions, present coverage report. Does all seem OK? If not...log.")
