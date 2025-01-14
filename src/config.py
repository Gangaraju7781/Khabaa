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
from typing import Dict, Optional
from pathlib import Path

class Config:
    """Configuration manager for the application"""
    
    @staticmethod
    def setup_google_credentials() -> str:
        """Set up Google credentials from Streamlit secrets"""
        credentials_json = st.secrets.get("GOOGLE_APPLICATION_CREDENTIALS")
        if not credentials_json:
            raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not found in Streamlit secrets.")
        
        try:
            # Convert AttrDict to a plain dictionary and ensure it's properly formatted
            credentials_dict = dict(credentials_json)
            
            # Create a secure temporary directory if it doesn't exist
            temp_dir = Path("/tmp/secure_credentials")
            temp_dir.mkdir(exist_ok=True, mode=0o700)
            
            # Write credentials to a temporary file with secure permissions
            credentials_path = temp_dir / "google_credentials.json"
            with open(credentials_path, "w", mode=0o600) as f:
                json.dump(credentials_dict, f)
                
            return str(credentials_path)
        except (json.JSONDecodeError, TypeError, AttributeError) as e:
            raise ValueError(f"Failed to process GOOGLE_APPLICATION_CREDENTIALS: {e}")

    @staticmethod
    def get_required_secret(key: str) -> str:
        """Get a required secret value and ensure it's a string"""
        value = st.secrets.get(key)
        if value is None:
            raise ValueError(f"Required secret '{key}' not found in Streamlit secrets.")
        return str(value)

    @staticmethod
    def get_optional_secret(key: str, default: str = "") -> str:
        """Get an optional secret value with a default"""
        value = st.secrets.get(key)
        return str(value) if value is not None else default

    @staticmethod
    def validate_spanner_config(instance_id: str, database_id: str) -> None:
        """Validate Spanner configuration values"""
        if not instance_id or not instance_id.strip():
            raise ValueError("INSTANCE_ID cannot be empty")
        if not database_id or not database_id.strip():
            raise ValueError("DATABASE_ID cannot be empty")

def load_config() -> Dict[str, str]:
    """Load and validate all configuration values"""
    try:
        # Set up Google credentials
        credentials_path = Config.setup_google_credentials()
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

        # Get required configurations
        instance_id = Config.get_required_secret("INSTANCE_ID")
        database_id = Config.get_required_secret("DATABASE_ID")
        
        # Validate Spanner configuration
        Config.validate_spanner_config(instance_id, database_id)
        
        # Get other configurations (optional with defaults)
        serp_api_key = Config.get_optional_secret("SERP_API_KEY")
        openai_api_key = Config.get_optional_secret("OPENAI_API_KEY")
        stripe_api_key = Config.get_optional_secret("STRIPE_API_KEY")
        
        # Return all configurations
        return {
            "GOOGLE_CREDENTIALS_PATH": credentials_path,
            "INSTANCE_ID": instance_id,
            "DATABASE_ID": database_id,
            "SERP_API_KEY": serp_api_key,
            "OPENAI_API_KEY": openai_api_key,
            "STRIPE_API_KEY": stripe_api_key
        }
    except Exception as e:
        st.error(f"Configuration Error: {str(e)}")
        raise

# Load the configuration
try:
    config = load_config()
    
    # Make configurations easily accessible
    instance_id = config["INSTANCE_ID"]
    database_id = config["DATABASE_ID"]
    api_key = config["SERP_API_KEY"]
    openai_api_key = config["OPENAI_API_KEY"]
    stripe_api_key = config["STRIPE_API_KEY"]
    
    # Optional: Add configuration status to sidebar for debugging
    if st.secrets.get("DEBUG", False):
        with st.sidebar.expander("Configuration Status", expanded=False):
            st.write("✅ Configuration loaded successfully")
            st.write("Connected to instance:", instance_id)
            
except Exception as e:
    st.error("Failed to load configuration. Please check your secrets and try again.")
    raise


# SMTP Configuration for Gmail
smtp_server = "smtp.gmail.com"
smtp_port = 587  # TLS port
smtp_username = "bhaskarabbireddy9@gmail.com"  # Your Gmail address
smtp_password = "ffkv owzp xbvb jbsf"  # App password or Gmail password

# OpenAI API Key
import openai
openai.api_key = openai_api_key
