import streamlit as st
from src.recipes import generate_recipes

def handle_home_click():
    st.session_state.page = 'main'
    st.session_state.search_done = False
    st.session_state.search_query = ''
    st.session_state.matched_products = []

def handle_cart_click():
    st.session_state.page = 'cart'

def handle_account_click():
    st.session_state.page = 'account'

def handle_generate_recipes():
    st.session_state.generated_recipes = generate_recipes(st.session_state.cart)
    st.session_state.show_generated_recipes = True

def handle_recipe_check():
    recipe_name = st.session_state.recipe_input
    if recipe_name:
        st.session_state.checked_recipe = generate_recipes(st.session_state.cart, recipe_name)
        st.session_state.show_checked_recipe = True
    else:
        st.warning("Please enter a recipe name.")

def handle_profile_click():
    st.session_state.page = 'profile'

def handle_wallet_click():
    st.session_state.page = 'wallet'

def handle_orders_click():
    st.session_state.page = 'orders'

def handle_subscriptions_click():
    st.session_state.page = 'subscriptions'

def handle_settings_click():
    st.session_state.page = 'settings'

def handle_logout_click():
    # Clear session state and navigate to login page
    st.session_state.clear()
    st.session_state.page = 'main'


