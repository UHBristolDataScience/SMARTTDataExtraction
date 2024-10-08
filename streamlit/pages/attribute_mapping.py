import streamlit as st
import time
from utilities import _hide_pages, load_example_data, mark_variable_as_mapped

st.set_page_config(layout='wide', initial_sidebar_state='collapsed')
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
priority = 0  # This column will be used to prioritise which attribute to use when a patient has a value recorded
              # for more than one attribute corresponding to the same schema variable on a given time point.
next_button = st.button("Save selection and proceed to next intervention.")

if next_button:
    temp = list(st.session_state.selected_interventions)
    # First try to save the attributes that have just been selected:
    try:
        # We save the selected attributes here:
        selected_attributes = st.session_state.edited_attribute_df.loc[
            st.session_state.edited_attribute_df.Select
        ][['attributeId', 'shortLabel', 'tableName']].copy()
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
        selected_attributes.insert(
            3, 'priority',
            priority
        )
        st.session_state.local_db.enter_df(
            df=selected_attributes,
            name='final_mapping',
            if_exists='append',
            index=False
        )
        if len(selected_attributes) == 0:
            st.warning('No attribute was selected!')
            time.sleep(2)
        else:
            priority += 1

    except (ValueError, IndexError):
        pass

    # Then try to progress to the next selected intervention for this schema variable:
    try:
        st.session_state['active_intervention_id'] = int(
            temp[temp.index(st.session_state.active_intervention_id) + 1]
        )

    # If end reached, save progress and go back to intervention_mapping
    except (ValueError, IndexError):
        mark_variable_as_mapped()
        st.success(
            """
            You have mapped all interventions for this variable!
            You will now return to select another variable to map...
            """
        )
        time.sleep(2)

        st.switch_page("pages/intervention_mapping.py")

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
df = load_example_data(attribute_id_list, add_median_iqr=True)
display_columns = st.session_state.config['app']['display_columns']

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


@st.dialog("Attribute Sample", width='small')
def view_attribute_sample():

    selected = st.session_state.edited_attribute_df.loc[
        st.session_state.edited_attribute_df.Select
    ]
    if len(selected) == 0 or len(selected) > 1:
        st.warning("Please select a single attribute to view a representative sample of values.")
    else:
        sample_attribute_id = selected.iloc[0].attributeId
        sample_data = st.session_state.local_db.query_pd(
            f"""
                    SELECT * FROM example_attribute_data
                    WHERE attributeId  = {sample_attribute_id}
                """
        )[st.session_state.config['app']['sample_columns']]
        st.write(sample_data)


if st.button("View sample", help="Click to view a sample of multiple values for a single selected attribute."):
    view_attribute_sample()

# st.text_input(
#     label="If you have any comments or observations, please enter them here."
# )

