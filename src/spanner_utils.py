import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import hashlib
import uuid
from google.cloud import spanner
import streamlit as st
from config import instance_id, database_id

# Initialize Spanner client
spanner_client = spanner.Client()

# Ensure instance_id and database_id are strings
instance = spanner_client.instance(str(instance_id))
database = instance.database(str(database_id))

# Product-related functions (original)
def product_exists(transaction, product_link):
    """
    Checks if the product already exists in the database (Google Cloud Spanner).
    """
    query = f"SELECT COUNT(1) FROM ProductsWithImages WHERE product_link = '{product_link}'"
    result = list(transaction.execute_sql(query))
    return result[0][0] > 0

def insert_data_to_spanner(data, instance_id, database_id):
    """
    Inserts the product data into the Spanner database.
    """
    spanner_client = spanner.Client()
    instance = spanner_client.instance(instance_id)
    database = instance.database(database_id)

    def insert_transaction(transaction):
        columns = ['product_id', 'product_details', 'product_link', 'price', 'number_of_ratings', 'description', 'values', 'image_url']
        rows = [(item['product_id'], item['product_details'], item['product_link'], item['price'], item['number_of_ratings'], item['description'], item['values'], item['image_url'])
                for item in data if not product_exists(transaction, item['product_link'])]
        if rows:
            transaction.insert(table='ProductsWithImages', columns=columns, values=rows)
            st.success(f"Inserted {len(rows)} new rows into the ProductsWithImages table.")

    database.run_in_transaction(insert_transaction)

def filter_products(preferences, query, instance_id, database_id):
    """
    Filter products from the Spanner database based on user selections of the filter and the search query.
    """
    spanner_client = spanner.Client()
    instance = spanner_client.instance(instance_id)
    database = instance.database(database_id)

    with database.snapshot() as snapshot:
        results = snapshot.execute_sql(
            "SELECT product_details, product_link, price, number_of_ratings, description, values, image_url "
            "FROM ProductsWithImages"
        )
        matched_products = []
        for row in results:
            if query.lower() in row[0].lower():
                values = row[5].split(', ')
                matches = sum([
                    preferences['gluten_free'] and 'gluten-free' in values,
                    preferences['vegan'] and 'vegan' in values,
                    preferences['organic'] and 'organic' in values
                ])
                matched_products.append({
                    'product_details': row[0],
                    'product_link': row[1],
                    'price': row[2],
                    'number_of_ratings': row[3],
                    'description': row[4],
                    'values': row[5],
                    'image_url': row[6],
                    'matches': matches
                })

        matched_products.sort(key=lambda x: x['matches'], reverse=True)

        for product in matched_products:
            del product['matches']

        return matched_products

# User authentication functions (updated)
def hash_password(password):
    """Hashes a password using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()

def user_exists(transaction, email):
    """Checks if a user exists by email."""
    query = "SELECT COUNT(1) FROM Users WHERE Email = @email"
    params = {"email": email}
    param_types = {"email": spanner.param_types.STRING}
    result = list(transaction.execute_sql(query, params=params, param_types=param_types))
    return result[0][0] > 0

def fetch_user_details(user_id):
    """Fetch user details including the profile picture."""
    spanner_client = spanner.Client()
    instance = spanner_client.instance(instance_id)
    database = instance.database(database_id)

    with database.snapshot() as snapshot:
        query = """
            SELECT FirstName, LastName, Email, ProfilePictureUrl
            FROM Users
            WHERE UserID = @user_id
        """
        params = {"user_id": user_id}
        param_types = {"user_id": spanner.param_types.STRING}
        result = list(snapshot.execute_sql(query, params=params, param_types=param_types))
        return result[0] if result else None
    
def update_user_details(user_id, first_name, last_name, email, password=None, profile_picture_url=None):
    """
    Update user details including profile picture in Google Cloud Spanner.
    
    Args:
        user_id (str): The unique identifier for the user
        first_name (str): User's first name
        last_name (str): User's last name
        email (str): User's email address
        password (str, optional): New password if being updated
        profile_picture_url (str, optional): URL to the user's profile picture
        
    Returns:
        bool: True if update successful, False otherwise
        
    Raises:
        Exception: If the update fails
    """
    spanner_client = spanner.Client()
    instance = spanner_client.instance(instance_id)
    database = instance.database(database_id)

    def update_transaction(transaction):
        # Prepare base parameters
        params = {
            "first_name": first_name,
            "last_name": last_name,
            "Email": email,
            "profile_picture_url": profile_picture_url,
            "user_id": user_id,
        }
        param_types = {
            "first_name": spanner.param_types.STRING,
            "last_name": spanner.param_types.STRING,
            "Email": spanner.param_types.STRING,
            "profile_picture_url": spanner.param_types.STRING,
            "user_id": spanner.param_types.STRING,
        }

        # Build the SQL query
        if password:
            hashed_password = hash_password(password)
            sql = """
                UPDATE Users
                SET FirstName = @first_name,
                    LastName = @last_name,
                    Email = @Email,
                    ProfilePictureUrl = @profile_picture_url,
                    PasswordHash = @password_hash
                WHERE UserID = @user_id
            """
            params["password_hash"] = hashed_password
            param_types["password_hash"] = spanner.param_types.STRING
        else:
            sql = """
                UPDATE Users
                SET FirstName = @first_name,
                    LastName = @last_name,
                    Email = @Email,
                    ProfilePictureUrl = @profile_picture_url
                WHERE UserID = @user_id
            """

        # Execute the update
        row_count = transaction.execute_update(
            sql,
            params=params,
            param_types=param_types
        )
        
        if row_count == 0:
            raise Exception("No user found with the provided ID")

    try:
        database.run_in_transaction(update_transaction)
        return True
    except Exception as e:
        st.error(f"Failed to update user details: {str(e)}")
        return False
    
def register_user(first_name, last_name, email, password):
    """Registers a new user in the database."""
    spanner_client = spanner.Client()
    instance = spanner_client.instance(instance_id)
    database = instance.database(database_id)

    def insert_user(transaction):
        if user_exists(transaction, email):
            raise ValueError("Email already exists.")
        user_id = str(uuid.uuid4())
        hashed_password = hash_password(password)
        columns = ["UserID", "FirstName", "LastName", "Email", "PasswordHash", "CreatedAt"]
        values = [user_id, first_name, last_name, email, hashed_password, spanner.COMMIT_TIMESTAMP]
        transaction.insert(table="Users", columns=columns, values=[values])

    try:
        database.run_in_transaction(insert_user)
        st.success("User registered successfully!")
    except ValueError as e:
        st.error(str(e))
    except Exception as e:
        st.error(f"An error occurred: {e}")

def authenticate_user(email, password):
    """Authenticates a user by email and password, and fetches their first name."""
    spanner_client = spanner.Client()
    instance = spanner_client.instance(instance_id)
    database = instance.database(database_id)

    def check_credentials(transaction):
        hashed_password = hash_password(password)
        query = (
            "SELECT UserID, FirstName FROM Users WHERE Email = @Email AND PasswordHash = @PasswordHash"
        )
        params = {"Email": email, "PasswordHash": hashed_password}
        param_types = {"Email": spanner.param_types.STRING, "PasswordHash": spanner.param_types.STRING}
        result = list(transaction.execute_sql(query, params=params, param_types=param_types))
        return result[0] if result else None

    with database.snapshot() as snapshot:
        user_data = check_credentials(snapshot)
        if user_data:
            st.session_state["user_id"] = user_data[0]
            st.session_state["first_name"] = user_data[1]  # Store first name in session state
            st.success(f"Welcome back, {user_data[1]}!")
            return True
        else:
            st.error("Email or password is incorrect.")
            return False

def subscribe_user_to_plan(user_id, plan_id, start_date, end_date):
    """Subscribes a user to a specific plan."""
    spanner_client = spanner.Client()
    instance = spanner_client.instance(instance_id)
    database = instance.database(database_id)

    def subscribe_user(transaction):
        columns = ["UserID", "PlanID", "StartDate", "EndDate", "CreatedAt"]
        values = [(user_id, plan_id, start_date, end_date, spanner.COMMIT_TIMESTAMP)]
        transaction.insert(table="UserSubscriptions", columns=columns, values=values)

    database.run_in_transaction(subscribe_user)
    st.success(f"User {user_id} subscribed to plan {plan_id}.")

def fetch_user_subscription(user_id):
    """Fetch the subscription plan details for a user."""
    spanner_client = spanner.Client()
    instance = spanner_client.instance(instance_id)
    database = instance.database(database_id)

    with database.snapshot() as snapshot:
        query = """
            SELECT SubscriptionPlans.PlanName, SubscriptionPlans.BillingCycle, SubscriptionPlans.Cost, SubscriptionPlans.Benefits
            FROM UserSubscriptions
            INNER JOIN SubscriptionPlans ON UserSubscriptions.PlanID = SubscriptionPlans.PlanID
            WHERE UserSubscriptions.UserID = @user_id
        """
        params = {"user_id": user_id}
        param_types = {"user_id": spanner.param_types.STRING}
        results = list(snapshot.execute_sql(query, params=params, param_types=param_types))
        return results[0] if results else None
