import streamlit as st

def initialize_session_state():
    if 'page' not in st.session_state:
        st.session_state.page = 'main'
    if 'preferences' not in st.session_state:
        st.session_state.preferences = {
            'gluten_free': False,
            'vegan': False,
            'organic': False
        }
    if 'cart' not in st.session_state:
        st.session_state.cart = []
    if 'generated_recipes' not in st.session_state:
        st.session_state.generated_recipes = []
    if 'checked_recipe' not in st.session_state:
        st.session_state.checked_recipe = []
    if 'show_generated_recipes' not in st.session_state:
        st.session_state.show_generated_recipes = False
    if 'show_checked_recipe' not in st.session_state:
        st.session_state.show_checked_recipe = False
    if 'email_address' not in st.session_state:
        st.session_state.email_address = ''
    if 'email_status' not in st.session_state:
        st.session_state.email_status = ''
    if 'search_done' not in st.session_state:
        st.session_state.search_done = False
    if 'search_query' not in st.session_state:
        st.session_state.search_query = ''
    if 'matched_products' not in st.session_state:
        st.session_state.matched_products = []
