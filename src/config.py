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

import os
import json
import streamlit as st
from typing import Dict

def write_credentials_file(credentials_dict: Dict) -> str:
    """
    Safely write credentials to a temporary file with proper permissions
    """
    try:
        # Create credentials directory if it doesn't exist
        os.makedirs("/tmp/credentials", exist_ok=True)
        credentials_path = "/tmp/credentials/google_credentials.json"
        
        # Write credentials with proper permissions
        with open(credentials_path, "w") as f:
            json.dump(credentials_dict, f)
        
        # Set proper file permissions (readable only by the current user)
        os.chmod(credentials_path, 0o600)
        
        return credentials_path
    except Exception as e:
        raise ValueError(f"Failed to write credentials file: {str(e)}")

def load_config() -> Dict[str, str]:
    """Load all configuration values from Streamlit secrets"""
    # Get Google credentials
    credentials = st.secrets.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not credentials:
        raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not found in secrets")
    
    try:
        # Handle both string and dictionary formats
        if isinstance(credentials, str):
            credentials_dict = json.loads(credentials)
        else:
            credentials_dict = dict(credentials)
            
        # Write credentials to file
        credentials_path = write_credentials_file(credentials_dict)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid GOOGLE_APPLICATION_CREDENTIALS format: {str(e)}")
    
    # Get other required configurations
    config = {
        "INSTANCE_ID": str(st.secrets.get("INSTANCE_ID", "")),
        "DATABASE_ID": str(st.secrets.get("DATABASE_ID", "")),
        "SERP_API_KEY": str(st.secrets.get("SERP_API_KEY", "")),
        "OPENAI_API_KEY": str(st.secrets.get("OPENAI_API_KEY", "")),
        "STRIPE_API_KEY": str(st.secrets.get("STRIPE_API_KEY", ""))
    }
    
    # Validate required configurations
    if not config["INSTANCE_ID"] or not config["DATABASE_ID"]:
        raise ValueError("INSTANCE_ID and DATABASE_ID must be provided in secrets")
        
    return config

# Load configuration
try:
    config = load_config()
    
    # Make configurations available globally
    instance_id = config["INSTANCE_ID"]
    database_id = config["DATABASE_ID"]
    api_key = config["SERP_API_KEY"]
    openai_api_key = config["OPENAI_API_KEY"]
    stripe_api_key = config["STRIPE_API_KEY"]
    
except Exception as e:
    st.error(f"Configuration Error: {str(e)}")
    raise


# SMTP Configuration for Gmail
smtp_server = "smtp.gmail.com"
smtp_port = 587  # TLS port
smtp_username = "bhaskarabbireddy9@gmail.com"  # Your Gmail address
smtp_password = "ffkv owzp xbvb jbsf"  # App password or Gmail password

# OpenAI API Key
import openai
openai.api_key = openai_api_key
