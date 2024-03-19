import streamlit as st
from utilities import _hide_pages

_hide_pages()
st.write(f"Selected interventions: {st.session_state.selected_interventions}")

st.write("We now step through each, and ask the user to select attributes. Also allows comments if something not right")
st.write("After completing all attributes and interventions, present coverage report. Does all seem OK? If not...log.")
