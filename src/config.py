# import os
# import json
# import streamlit as st

# # Fetch credentials from Streamlit secrets
# credentials_json = st.secrets["GOOGLE_APPLICATION_CREDENTIALS"]

# if credentials_json:
#     try:
#         # Convert AttrDict to a plain dictionary
#         credentials_dict = dict(credentials_json)

#         # Write credentials to a temporary file
#         credentials_path = "/tmp/google_credentials.json"
#         with open(credentials_path, "w") as f:
#             json.dump(credentials_dict, f)
        
#         # Set the environment variable to point to the temporary file
#         os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
#     except json.JSONDecodeError as e:
#         raise ValueError(f"Failed to decode GOOGLE_APPLICATION_CREDENTIALS: {e}")
# else:
#     raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not found in Streamlit secrets.")

# # Fetch other secrets and convert to strings
# instance_id = st.secrets['INSTANCE_ID']
# database_id = st.secrets['DATABASE_ID']
# api_key = st.secrets['SERP_API_KEY']
# openai_api_key = st.secrets['OPENAI_API_KEY']
# stripe_api_key = st.secrets['STRIPE_API_KEY']

# config.py
import os
import json
import streamlit as st
from google.cloud import spanner

def setup_google_credentials():
    """Setup Google credentials from Streamlit secrets"""
    credentials_json = st.secrets.get("GOOGLE_APPLICATION_CREDENTIALS")
    if credentials_json:
        try:
            # Convert AttrDict to dict if needed
            credentials_dict = dict(credentials_json) if hasattr(credentials_json, '__dict__') else credentials_json
            credentials_path = "/tmp/google_credentials.json"
            with open(credentials_path, "w") as f:
                json.dump(credentials_dict, f)
            os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        except Exception as e:
            raise ValueError(f"Failed to process GOOGLE_APPLICATION_CREDENTIALS: {e}")
    else:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not found in Streamlit secrets")

def get_spanner_configs():
    """Get and validate Spanner configurations"""
    # Convert AttrDict to string explicitly
    instance_id = str(st.secrets["INSTANCE_ID"])
    database_id = str(st.secrets["DATABASE_ID"])
    return instance_id, database_id

def get_spanner_client():
    """Initialize and return Spanner client, instance, and database"""
    try:
        # Initialize client
        client = spanner.Client()
        
        # Get instance and database IDs
        instance_id, database_id = get_spanner_configs()
        
        # Get instance and database
        instance = client.instance(instance_id)
        database = instance.database(database_id)
        
        return client, instance, database
    except Exception as e:
        raise ValueError(f"Failed to initialize Spanner client: {e}")

def authenticate_user(email, password):
    """Authenticate user with email and password"""
    try:
        # Get Spanner database
        _, _, database = get_spanner_client()
        
        # Hash password
        hashed_password = hashlib.sha256(password.encode()).hexdigest()
        
        # Execute query within snapshot
        with database.snapshot() as snapshot:
            query = """
                SELECT UserID, FirstName 
                FROM Users 
                WHERE Email = @email 
                AND PasswordHash = @password_hash
            """
            
            params = {
                'email': email,
                'password_hash': hashed_password
            }
            param_types = {
                'email': spanner.param_types.STRING,
                'password_hash': spanner.param_types.STRING
            }
            
            results = list(snapshot.execute_sql(
                query,
                params=params,
                param_types=param_types
            ))
            
            if results:
                user_id, first_name = results[0]
                st.session_state["user_id"] = user_id
                st.session_state["first_name"] = first_name
                st.success(f"Welcome back, {first_name}!")
                return True
            else:
                st.error("Invalid email or password.")
                return False
                
    except Exception as e:
        st.error(f"Authentication error: {str(e)}")
        return False

# Initialize the configuration when the module is imported
try:
    setup_google_credentials()
except Exception as e:
    st.error(f"Failed to setup Google credentials: {e}")
    raise

# SMTP Configuration for Gmai
