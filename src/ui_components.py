import streamlit as st
from src.handlers import (
    handle_home_click, handle_cart_click, handle_account_click, 
    handle_profile_click, handle_wallet_click, handle_orders_click, 
    handle_subscriptions_click, handle_settings_click, handle_logout_click
)
from src.utilss import calculate_cart_total

def proceed_to_checkout():
    st.session_state.page = 'checkout'
    st.experimental_rerun()

def render_buttons():
    col1, col2, col3, col4, col5 = st.columns([1, 8, 2, 0.98, 0.75])

    with col1:
        st.button('Home', on_click=handle_home_click)
    with col4:
        st.button('Cart', on_click=handle_cart_click)
    with col5:
        if "first_name" in st.session_state and st.session_state["first_name"]:
            dropdown_label = f"Hi, {st.session_state['first_name']}"
            
            # Style adjustments
            expander_style = """
                <style>
                .stExpander > div:first-child {
                    width: 200px; /* Adjust width to match options */
                    text-align: center; /* Center align text */
                }
                .stExpander > div > div {
                    border: 1px solid #d3d3d3; /* Add border around expander */
                    border-radius: 5px;
                    padding: 5px;
                }
                </style>
            """
            st.markdown(expander_style, unsafe_allow_html=True)
            
            with st.expander(dropdown_label):
                button_style = """
                    <style>
                    .stButton > button {
                        background-color: white; 
                        color: black; 
                        border: 1px solid #d3d3d3; 
                        border-radius: 5px;
                        margin: 2px 0; /* Reduce gap between buttons */
                        width: 180px; /* Ensure buttons are of uniform width */
                    }
                    .stButton > button:hover {
                        background-color: #f0f0f0;
                    }
                    </style>
                """
                st.markdown(button_style, unsafe_allow_html=True)

                st.button("Profile", on_click=handle_profile_click)
                st.button("Wallet", on_click=handle_wallet_click)
                st.button("Order History", on_click=handle_orders_click)
                st.button("Subscriptions", on_click=handle_subscriptions_click)
                st.button("Settings", on_click=handle_settings_click)
                
                # Logout button styled differently
                # Logout button styled differently
                logout_style = """
                    <style>
                    .logout-btn > button {
                        background-color: #ffcccc; 
                        color: #ff0000; 
                        border: 1px solid #ff8080; 
                        border-radius: 5px;
                        width: 180px;
                    }
                    .logout-btn > button:hover {
                        background-color: #ff9999;
                    }
                    </style>
                """
                st.markdown(logout_style, unsafe_allow_html=True)
                logout_placeholder = st.container()
                with logout_placeholder:
                    st.button("Logout", on_click=handle_logout_click, key="logout_button")
            
def render_sidebar():
    with st.sidebar:
        # Cart Overview Section
        st.markdown("<h3 style='font-size: 22px;'>Cart Overview</h3>", unsafe_allow_html=True)

        # Check if the cart exists in session state
        if 'cart' in st.session_state and st.session_state.cart:
            total_amount = 0
            # Loop through items in the cart and display product name * quantity
            for item in st.session_state.cart:
                quantity = item.get('quantity', 1)
                price_per_item = float(item['price'].replace('USD', '').strip())
                item_total = price_per_item * quantity
                total_amount += item_total
                st.write(f"{item['product_details']} X {quantity} - USD {item_total:.2f}")
            
            # Display total amount
            st.write(f"**Total Amount:** USD {total_amount:.2f}")
            if st.button("Proceed to Checkout", key="sidebar_proceed_checkout"):
                proceed_to_checkout()


        else:
            st.write("Your cart is empty.")

        # Add some spacing between the sections
        st.write("")  # Empty string for small space
        st.markdown("<hr>", unsafe_allow_html=True)  # Horizontal line for separation
        st.write("")  # Another empty string for more space

        # Cuisine Selection Section
        st.markdown("<h3 style='font-size: 22px;'>Cuisine Selection</h3>", unsafe_allow_html=True)
        available_cuisines = [
            "Italian", "Indian", "Mexican", "Mediterranean", "Thai", "Japanese", "American"
        ]

        # Use a temporary variable to hold the selection
        selected_cuisines_temp = st.multiselect("Select cuisines for meal plan:", available_cuisines, key="cuisine_selection")

        # Apply button to store selected cuisines in session state
        if st.button("Apply", key="apply_cuisines"):
            if not selected_cuisines_temp:
                st.warning("No cuisines selected. Do you want to proceed with default?")
                st.session_state.cuisine_warning_shown = True
            else:
                st.session_state.selected_cuisines = selected_cuisines_temp
                st.success(f"Selected cuisines: {', '.join(selected_cuisines_temp)}")

        # Budget Section
        st.markdown("<h3 style='font-size: 22px;'>Budget Tracker</h3>", unsafe_allow_html=True)
        st.session_state.weekly_budget = st.number_input("Weekly Grocery Budget", min_value=0, value=st.session_state.weekly_budget)
        st.session_state.monthly_budget = st.number_input("Monthly Grocery Budget", min_value=0, value=st.session_state.monthly_budget)

        cart_total = calculate_cart_total()

        # Weekly Budget Calculation
        remaining_weekly_budget = st.session_state.weekly_budget - cart_total
        percent_used_weekly = (cart_total / st.session_state.weekly_budget) * 100 if st.session_state.weekly_budget else 0
        bar_color_weekly = "#00FF00" if remaining_weekly_budget >= 0 else "#FF0000"
        st.write("This Week's Spending:")
        st.write(f"You are ${-remaining_weekly_budget:.2f} over this week's budget." if remaining_weekly_budget < 0 else f"You have ${remaining_weekly_budget:.2f} left in this week's budget.")
        st.markdown(f"""<div style="background-color:lightgray;border-radius:5px;"><div style="width:{min(100, percent_used_weekly)}%;background-color:{bar_color_weekly};height:20px;border-radius:5px;"></div></div>""", unsafe_allow_html=True)

        # Monthly Budget Calculation
        remaining_monthly_budget = st.session_state.monthly_budget - cart_total
        percent_remaining_monthly = (cart_total / st.session_state.monthly_budget) * 100 if st.session_state.monthly_budget else 0
        bar_color_monthly = "#00FF00" if remaining_monthly_budget >= 0 else "#FF0000"
        st.write("")
        st.write("Remaining Budget for the Month:")
        st.write(f"You are ${-remaining_monthly_budget:.2f} over this month's budget." if remaining_monthly_budget < 0 else f"You have ${remaining_monthly_budget:.2f} left in this month's budget.")
        st.markdown(f"""<div style="background-color:lightgray;border-radius:5px;"><div style="width:{min(100, percent_remaining_monthly)}%;background-color:{bar_color_monthly};height:20px;border-radius:5px;"></div></div>""", unsafe_allow_html=True)
        st.write("")
        st.write(f"Total Cart Value: ${cart_total:.2f}")
        st.write(f"Current Weekly Limit: ${st.session_state.weekly_budget:.2f}")
        st.write(f"Monthly Limit Balance: ${remaining_monthly_budget:.2f}")

        # Reset budget limits button
        if st.button("Reset Budget Limits"):
            st.session_state.weekly_budget = 0
            st.session_state.monthly_budget = 0
            st.experimental_rerun()

        st.write("")  # Empty string for small space
        st.markdown("<hr>", unsafe_allow_html=True)  # Horizontal line for separation
        st.write("")  # Another empty string for more space

        # Time Tracker Section
        st.markdown("<h3 style='font-size: 22px;'>Time Tracker</h3>", unsafe_allow_html=True)
        st.session_state.min_time = st.number_input("Minimum Cooking Time (minutes)", min_value=0, value=st.session_state.min_time)
        st.session_state.max_time = st.number_input("Maximum Cooking Time (minutes)", min_value=0, value=st.session_state.max_time)

        # Reset time limits button
        if st.button("Reset Time Limits"):
            st.session_state.min_time = 0
            st.session_state.max_time = 0
            st.experimental_rerun()

def render_modal():
    st.markdown(
        '''
        <style>
        .modal-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.6);
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .modal-content {
            background: white;
            padding: 20px;
            border-radius: 8px;
        }
        </style>
        ''', unsafe_allow_html=True
    )
    st.markdown(
        '<div class="modal-overlay"><div class="modal-content"><h4>Modal Title</h4><p>Modal Content Here...</p><button onclick="window.location.href=\'#\'">Close</button></div></div>',
        unsafe_allow_html=True
    )
