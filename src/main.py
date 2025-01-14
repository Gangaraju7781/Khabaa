import streamlit as st
import os
import sys
from difflib import SequenceMatcher
from openai import APIConnectionError, RateLimitError, APIStatusError
from streamlit_lottie import st_lottie
import requests
import json

# Include the project directory in the Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import custom modules
from src.session_manager import initialize_session_state
from src.config import instance_id, database_id, api_key, openai_api_key
from src.ui_components import render_buttons, render_sidebar, render_modal
from src.handlers import handle_recipe_check
from src.email_utils import validate_email, send_email
from src.api import fetch_search_results
from src.spanner_utils import insert_data_to_spanner, filter_products, register_user, authenticate_user
from src.product import parse_search_results
from src.llm_utils import initialize_llm, parse_ingredient_with_llm
from src.recipes import generate_weekly_meal_plan
from src.checkout import checkout_page

# Streamlit page configuration
st.set_page_config(page_title="MarketPlace", layout="wide")

# Initialize session state variables
initialize_session_state()

# Initialize the OpenAI client with the API key
llm_client = initialize_llm(openai_api_key)


# Ensure session states
if 'unavailable_ingredients' not in st.session_state:
    st.session_state.unavailable_ingredients = []
if 'weekly_budget' not in st.session_state:
    st.session_state.weekly_budget = 0
if 'monthly_budget' not in st.session_state:
    st.session_state.monthly_budget = 0
if 'min_time' not in st.session_state:
    st.session_state.min_time = 0
if 'max_time' not in st.session_state:
    st.session_state.max_time = 0
if 'trigger_rerun' not in st.session_state:
    st.session_state.trigger_rerun = False
if 'selected_cuisines' not in st.session_state:
    st.session_state.selected_cuisines = []
if 'cuisine_warning_shown' not in st.session_state:
    st.session_state.cuisine_warning_shown = False
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'show_password' not in st.session_state:
    st.session_state.show_password = False

# Function to load Lottie animations
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()

def load_lottie_file(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)
    
# Load a grocery-related Lottie animation
lottie_animation = load_lottie_file("/Users/bdvvgangarajuabbireddy/Downloads/grocery_animation.json")

def proceed_to_checkout():
    st.session_state.page = 'checkout'
    st.experimental_rerun()

# Custom CSS Styling
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(to bottom, #e3f2fd, #ffffff);
        font-family: 'Roboto', sans-serif;
        padding: 0;
        margin: 0;
        width: 100%; /* Ensures full-page width */
        box-sizing: border-box; /* Includes padding and border in width */
    }

    /* Center logo and welcome text */
    .logo-container {
        display: block; /* Simple block layout */
        text-align: center; /* Center horizontally */
        margin-bottom: 20px; /* Adjust as needed */
    }
    .logo-container img {
        max-width: 300px;
        height: auto;
    }

    /* Center welcome text */
    .welcome-text {
        text-align: center;
        color: #37474f;
        margin: 0;
        padding: 10px 0;
    }

    /* Center animation using CSS Grid */
    .animation-container {
        display: grid; /* Grid layout for centering */
        place-items: center; /* Center vertically and horizontally */
        height: 300px;
        margin: 0 auto;
        background: transparent; /* No background */
        padding: 0; /* Remove any extra padding */
    }

    /* Tabs styling */
    .stTabs {
        background: transparent;
    }
    .stTabs-tab {
        background-color: transparent !important;
    }

    /* Remove white container backgrounds */
    .element-container, .stMarkdown {
        background: transparent !important;
    }

    /* Style text inputs */
    .stTextInput>div>div {
        background-color: white;
        border-radius: 5px;
    }

    /* Button styling */
    .stButton>button {
        background-color: #4CAF50; /* Green button color */
        color: white;
        font-size: 16px;
        border: none;
        border-radius: 5px;
        padding: 10px 20px;
        cursor: pointer;
        transition: all 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #45a049; /* Darker green on hover */
    }

    .custom-logo {
        display: block; /* Turns the image into a block-level element */
        margin-left: auto; /* Center align horizontally */
        margin-right: auto; /* Center align horizontally */
        max-width: 500px; /* Adjust the size */
        height: auto; /* Maintain aspect ratio */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Modify the logo and welcome message display
if st.session_state.user_id is None:
    st.markdown("<div class='logo-container'><img src='https://t4.ftcdn.net/jpg/01/95/78/87/360_F_195788717_Ba8397mYBadW3JUx5SQejAxpRN02DyEF.jpg' alt='Marketplace Logo' style='max-width: 500px; height: auto;'></div>", unsafe_allow_html=True)
    st.markdown("<h1 class='welcome-text'>Welcome to the Marketplace!</h1>", unsafe_allow_html=True)
    if lottie_animation:
        st.markdown("<div class='lottie-container'>", unsafe_allow_html=True)
        st_lottie(lottie_animation, height=300, key="welcome_animation")  # Increased height
        st.markdown("</div>", unsafe_allow_html=True)

# Modify the tabs section
if st.session_state.user_id is None:
    tabs = st.tabs(["Login", "Register"])

    with tabs[1]:  # Register Tab
        st.subheader("Create an account")
        first_name = st.text_input("First Name", placeholder="Enter your first name", key="register_first_name")
        last_name = st.text_input("Last Name", placeholder="Enter your last name", key="register_last_name")
        email = st.text_input("Email", placeholder="Enter your email", key="register_email")
        password = st.text_input("Password", placeholder="Create a password", type="password", key="register_password")
        if st.button("Register", key="register_button"):
            if first_name and last_name and email and password:
                register_user(first_name, last_name, email, password)
                st.success("Registration successful! Please log in.")
            else:
                st.warning("Please fill all fields.")

    with tabs[0]:  # Login Tab
        st.subheader("Login to your Account")
        email = st.text_input("Email", placeholder="Enter your email", key="login_email")
        password_type = "text" if st.session_state.show_password else "password"
        password = st.text_input("Password", placeholder="Enter your password", type=password_type, key="login_password")
        if st.checkbox("Show Password", key="login_show_password_checkbox"):
            st.session_state.show_password = not st.session_state.show_password
        if st.button("Login", key="login_button"):
            if email and password:
                if authenticate_user(email, password):
                    st.success("Login successful!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid email or password.")
            else:
                st.warning("Please enter both email and password.")
        st.markdown("<p style='text-align: center;'>Forgot your password? <a href='#'>Click here</a></p>", unsafe_allow_html=True)

else:
    # Main Marketplace Page Logic
    render_buttons()
    render_sidebar()


    def is_similar(ingredient, product_name, threshold=0.7):
        return SequenceMatcher(None, ingredient.lower(), product_name.lower()).ratio() > threshold

    if st.session_state.page == 'main':
        st.markdown('<img src="https://t4.ftcdn.net/jpg/01/95/78/87/360_F_195788717_Ba8397mYBadW3JUx5SQejAxpRN02DyEF.jpg" class="custom-logo">', unsafe_allow_html=True)
        # st.markdown('<h1 style="text-align: center;">Welcome to the Marketplace!</h1>', unsafe_allow_html=True)
        query = st.text_input("Enter your search query:", key='search_query')
        num_searches = st.radio("Number of Search Results:", (5, 10, 15, 20), index=1, key='num_searches')

        st.markdown("### Preferences")
        st.session_state.preferences['gluten_free'] = st.checkbox("Gluten-free", st.session_state.preferences.get('gluten_free', False))
        st.session_state.preferences['vegan'] = st.checkbox("Vegan", st.session_state.preferences.get('vegan', False))
        st.session_state.preferences['organic'] = st.checkbox("Organic", st.session_state.preferences.get('organic', False))

        if st.button("Search"):
            if query:
                search_results = fetch_search_results(query, num_searches, api_key)
                if search_results:
                    products = parse_search_results(search_results, num_searches)
                    if products:
                        insert_data_to_spanner(products, instance_id, database_id)
                        st.session_state.search_done = True
                        st.session_state.matched_products = filter_products(st.session_state.preferences, query, instance_id, database_id)
                        st.session_state.trigger_rerun = True
                else:
                    st.warning("No search results found.")
            else:
                st.warning("Please enter a search query.")

        if st.session_state.search_done:
            st.header("Product Assistant")
            matched_products = st.session_state.matched_products
            if matched_products:
                st.write("Here are the products that match your preferences:")
                for product in matched_products:
                    col1, col2, col3 = st.columns([1, 3, 1])
                    with col1:
                        st.image(product['image_url'], use_column_width=True)
                    with col2:
                        st.write(f"**{product['product_details']}**")
                        st.write(f"Link: [Product Link]({product['product_link']})")
                        st.write(f"Price: {product['price']}")
                        st.write(f"Number of Ratings: {product['number_of_ratings']}")
                        st.write(f"Description: {product['description']}")
                        st.write(f"Values: {product['values']}")
                    with col3:
                        if st.button("Add to Cart", key=product['product_link']):
                            if 'cart' not in st.session_state:
                                st.session_state.cart = []
                            existing_product = next((item for item in st.session_state.cart if item['product_details'] == product['product_details']), None)
                            if existing_product:
                                existing_product['quantity'] += 1
                            else:
                                product['quantity'] = 1
                                st.session_state.cart.append(product)
                            st.success(f"Added {product['product_details']} to cart")
                            st.session_state.trigger_rerun = True
                    st.write("************")
            else:
                st.write("No products match your preferences.")


    #Cart page logic
    if st.session_state.page == 'cart':
        st.markdown('<img src="https://t4.ftcdn.net/jpg/01/95/78/87/360_F_195788717_Ba8397mYBadW3JUx5SQejAxpRN02DyEF.jpg" class="custom-logo">', unsafe_allow_html=True)
        st.header("Your Cart")

        if st.session_state.cart:
            for index, product in enumerate(st.session_state.cart):
                if 'quantity' not in product:
                    product['quantity'] = 1

                col1, col2, col3, col4, col5 = st.columns([1, 4, 2, 1, 1])
                with col1:
                    st.image(product['image_url'], width=100)
                with col2:
                    st.text(product['product_details'])
                with col3:
                    quantity = st.number_input("Quantity", min_value=1, value=product['quantity'], key=f"qty_{index}")
                    if quantity != product['quantity']:
                        product['quantity'] = quantity
                        st.session_state.trigger_rerun = True
                with col4:
                    price_per_item = float(product['price'].replace('USD', '').replace('$', '').replace(',', '').strip())
                    total_price = price_per_item * product['quantity']
                    st.markdown(f'<div class="price-large">USD {total_price:.2f}</div>', unsafe_allow_html=True)
                with col5:
                    if st.button("Remove", key=f"remove_{index}"):
                        st.session_state.cart.pop(index)
                        st.session_state.trigger_rerun = True
                st.write("----------")

                            # Proceed to Checkout Button
                if st.button("Proceed to Checkout", key="main_proceed_checkout"):
                    proceed_to_checkout()

                # Weekly Meal Plan Generation Button
                if st.button("Generate Weekly Meal Plan"):
                    selected_cuisines = st.session_state.selected_cuisines

                    # If no cuisines are selected, show alert and set the warning flag
                    if not selected_cuisines:
                        st.session_state.cuisine_warning_shown = True
                        st.warning("No cuisines selected. Do you want to proceed with default cuisines?")
                    else:
                        # Generate the meal plan with selected cuisines
                        min_time = st.session_state.min_time
                        max_time = st.session_state.max_time
                        st.session_state.meal_plan = generate_weekly_meal_plan(
                            st.session_state.cart, selected_cuisines, min_time, max_time
                        )
                        st.session_state.trigger_rerun = True

                # Handle the warning and confirmation for proceeding without selected cuisines
                if st.session_state.cuisine_warning_shown:
                    col1, col2 = st.columns([1, 1])
                    
                    # Confirmation to proceed with default cuisines
                    with col1:
                        if st.button("Yes, proceed with default cuisines"):
                            default_cuisines = [
                                "Italian", "Indian", "Mexican", "Mediterranean",
                                "Thai", "Japanese", "American"
                            ]
                            st.session_state.selected_cuisines = default_cuisines
                            st.session_state.cuisine_warning_shown = False  # Reset flag
                            
                            # Generate the meal plan with default cuisines
                            min_time = st.session_state.min_time
                            max_time = st.session_state.max_time
                            st.session_state.meal_plan = generate_weekly_meal_plan(
                                st.session_state.cart, default_cuisines, min_time, max_time
                            )
                            st.session_state.trigger_rerun = True

                    # Option to go back and select cuisines
                    with col2:
                        if st.button("No, go back to select cuisines"):
                            st.warning("Please select your preferred cuisines.")
                            st.session_state.cuisine_warning_shown = False  # Reset flag

                # Trigger rerun if necessary
                if st.session_state.trigger_rerun:
                    st.session_state.trigger_rerun = False
                    st.experimental_rerun()

            # Display generated meal plan
            if 'meal_plan' in st.session_state and st.session_state.meal_plan:
                st.header("Weekly Meal Plan")
                missing_ingredients_set = set()

                for meal in st.session_state.meal_plan:
                    st.write(f"**{meal['name']}**")
                    st.write(meal['details'])

                    if meal['missing_ingredients']:
                        missing_ingredients_set.update(meal['missing_ingredients'])

                if missing_ingredients_set:
                    st.write("### Missing Ingredients from all Recipes:")
                    missing_ingredients = list(missing_ingredients_set)
                    for i, ingredient in enumerate(missing_ingredients):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"- {ingredient}")
                        with col2:
                            if st.button(f"Add {ingredient} to Cart", key=f"add_to_cart_missing_{i}"):
                                cleaned_ingredient = parse_ingredient_with_llm(llm_client, ingredient)
                                try:
                                    search_results = fetch_search_results(cleaned_ingredient, 10, api_key)
                                    if search_results:
                                        products = parse_search_results(search_results, 10)
                                        if products:
                                            products[0]['quantity'] = 1
                                            st.session_state.cart.append(products[0])
                                            insert_data_to_spanner([products[0]], instance_id, database_id)
                                            st.success(f"Added {products[0]['product_details']} to cart")
                                        else:
                                            st.warning(f"No products available for '{ingredient}'")
                                    else:
                                        st.warning(f"No search results found for '{ingredient}'")
                                except (APIConnectionError, RateLimitError, APIStatusError) as e:
                                    st.error(f"Error adding ingredient: {str(e)}")
        else:
            st.write("Your cart is empty.")
        
         # Checkout Page Logic
        # if st.session_state.page == 'checkout':
        #     st.header("Checkout")


        st.header("Recipe Assistant: Generate Ingredients & Instructions")
        st.text_input("Enter a recipe name to check missing ingredients...", key="recipe_input")
        if st.button("Check Recipe", key="check_recipe"):
            st.session_state.unavailable_ingredients = []
            handle_recipe_check()
            st.session_state.trigger_rerun = True

        if st.session_state.show_checked_recipe:
            st.header("Recipe Check Results")
            if st.session_state.checked_recipe:
                for recipe in st.session_state.checked_recipe:
                    st.markdown(f"<h2>{recipe['name']}</h2>", unsafe_allow_html=True)
                    if 'Ingredients Missing:' in recipe['details']:
                        st.write("**Ingredients in Your Cart:**")
                        if 'cart' in st.session_state and st.session_state.cart:
                            cart_ingredients = [item['product_details'] for item in st.session_state.cart]
                            for ingredient in cart_ingredients:
                                st.write(f"- {ingredient}")
                        else:
                            st.write("None")
                        st.write("**Ingredients Missing:**")

                        details = recipe['details']
                        start_idx = details.find('Ingredients Missing:')
                        end_idx = details.find('Instructions:')
                        ingredients_missing_text = details[start_idx + len('Ingredients Missing:'):end_idx].strip()
                        ingredients_missing = [i.strip() for i in ingredients_missing_text.split('\n') if i.strip()]

                        for i, ingredient in enumerate(ingredients_missing):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.write(f"- {ingredient}")
                            with col2:
                                if st.button(f"Add to Cart", key=f"add_to_cart_{i}"):
                                    if 'cart' not in st.session_state:
                                        st.session_state.cart = []
                                    cleaned_ingredient = parse_ingredient_with_llm(llm_client, ingredient)
                                    st.info(f"Cleaned ingredient: {cleaned_ingredient}")
                                    try:
                                        search_results = fetch_search_results(cleaned_ingredient, 10, api_key)
                                        if search_results:
                                            products = parse_search_results(search_results, 10)
                                            if products:
                                                products[0]['quantity'] = 1
                                                st.session_state.cart.append(products[0])
                                                insert_data_to_spanner([products[0]], instance_id, database_id)
                                                st.success(f"Added {products[0]['product_details']} to cart")
                                                st.session_state.trigger_rerun = True
                                            else:
                                                st.warning(f"No products available for '{cleaned_ingredient}' after parsing.")
                                                st.session_state.unavailable_ingredients.append(ingredient)
                                        else:
                                            st.warning(f"No search results found for '{cleaned_ingredient}'.")
                                            st.session_state.unavailable_ingredients.append(ingredient)
                                    except (APIConnectionError, RateLimitError, APIStatusError) as e:
                                        st.error(f"Error fetching ingredient: {str(e)}")

                        if st.button("Add All Items to Cart"):
                            st.session_state.unavailable_ingredients = []
                            for ingredient in ingredients_missing:
                                cleaned_ingredient = parse_ingredient_with_llm(llm_client, ingredient)
                                st.info(f"Cleaned ingredient: {cleaned_ingredient}")
                                try:
                                    search_results = fetch_search_results(cleaned_ingredient, 10, api_key)
                                    if search_results:
                                        product = parse_search_results(search_results, 1)
                                        if product:
                                            product[0]['quantity'] = 1
                                            st.session_state.cart.append(product[0])
                                            insert_data_to_spanner([product[0]], instance_id, database_id)
                                        else:
                                            st.session_state.unavailable_ingredients.append(ingredient)
                                    else:
                                        st.session_state.unavailable_ingredients.append(ingredient)
                                except (APIConnectionError, RateLimitError, APIStatusError) as e:
                                    st.error(f"Error adding ingredient: {str(e)}")

                            cart_ingredients = [item['product_details'] for item in st.session_state.cart]
                            not_added_ingredients = [ingredient for ingredient in ingredients_missing if not any(is_similar(ingredient, product) for product in cart_ingredients)]
                            st.session_state.unavailable_ingredients.extend(not_added_ingredients)

                            st.session_state.trigger_rerun = True

                if 'details' in locals():
                    st.markdown("**Instructions:**")
                    st.write(details[end_idx:].strip().replace('**', '').strip())

                st.text_input("Enter your email to receive the recipes:", key="email_address_check")
                if st.button("Send Checked Recipe via Email"):
                    if validate_email(st.session_state.email_address_check):
                        send_email(st.session_state.checked_recipe, st.session_state.email_address_check)
                    else:
                        st.session_state.email_status = "Incorrect email address"
                    st.write(st.session_state.email_status)
            else:
                st.write("No missing ingredients found.")

            if st.session_state.unavailable_ingredients:
                st.markdown("### Ingredients not available at the moment")
                for ingredient in st.session_state.unavailable_ingredients:
                    st.write(f"- {ingredient}")

    elif st.session_state.page == 'account':
        st.header("Your Account")

    elif st.session_state.page == 'checkout':
        checkout_page()

    # Render modal if necessary
    if st.session_state.page == 'modal':
        render_modal()

    # Check for trigger rerun flag and call rerun
    if st.session_state.trigger_rerun:
        st.session_state.trigger_rerun = False
        st.experimental_rerun()


if st.session_state.page == 'profile':
    from user_profile import profile_page
    profile_page()

elif st.session_state.page == 'wallet':
    st.header("Your Wallet")

elif st.session_state.page == 'orders':
    st.header("Order History")

elif st.session_state.page == 'subscriptions':
    from subscription import subscription_page
    subscription_page()

elif st.session_state.page == 'settings':
    st.header("Settings")

