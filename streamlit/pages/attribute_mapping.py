import streamlit as st
import time
from utilities import _hide_pages, load_example_data

# TODO: ask user to also select data column? e.g. checkbox column "IsString"
# TODO: implement refresh data to get a new sample of example attribute data (pass new random satte to load method)
#     note: this will clear existing selections.
# TODO: After completing all attributes and interventions, present coverage report. Does all seem OK? If not...log.
# TODO: Handle selection of intervention with no example data? (shouldn't happen in theory...)
_hide_pages()
st.title("Variable mapping")
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

next_button = st.button("Save selection and proceed to next intervention.")

if next_button:
    temp = list(st.session_state.selected_interventions)
    try:
        # We save the selected attributes here:
        selected_attributes = st.session_state.edited_attribute_df.loc[
            st.session_state.edited_attribute_df.Select
        ][['attributeId', 'shortLabel']].copy()
        selected_attributes.rename(
            columns={'shortLabel': 'attributeShortLabel'}, inplace=True
        )
        selected_attributes.insert(
            0, 'schemaVariable',
            st.session_state.active_variable
        )
        selected_attributes.insert(
            1, 'interventionId',
            int(st.session_state.active_intervention_id)
        )
        selected_attributes.insert(
            2, 'interventionLongLabel',
            st.session_state.selected_interventions[st.session_state.active_intervention_id]
        )
        st.write(selected_attributes)

        st.session_state['active_intervention_id'] = int(
            temp[temp.index(st.session_state.active_intervention_id) + 1]
        )

    except (ValueError, IndexError):
        st.session_state.local_db.insert_query(
            f"""
                    UPDATE schema
                    SET mapping_complete = True
                    WHERE "Variable" = "{st.session_state.active_variable}";
                """
        )
        progress = 1 / len(st.session_state.schema)
        st.session_state.local_db.insert_query(
            f"""
                    UPDATE info
                    SET variable_mapping_progress = variable_mapping_progress + {progress}
                    WHERE "name" = "{st.session_state.project_name}";
                """
        )
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
attribute_id_list = list(
    st.session_state.local_db.query_pd(
        f"""
            SELECT attributeId
            FROM distinct_attributes
            WHERE interventionId="{st.session_state['active_intervention_id']}" 
        """
    ).attributeId
)
df = load_example_data(attribute_id_list)
display_columns = ['attributeId', 'shortLabel', 'valueNumber', 'valueString', 'unitOfMeasure']

attribute_df = df[display_columns].copy()
attribute_df.insert(0, 'Select', False)

st.session_state['edited_attribute_df'] = st.data_editor(
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
# TODO: implement saving comments:
st.text_input(
    label="If you have any comments or observations, please enter them here."
)

