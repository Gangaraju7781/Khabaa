import os
import json
import streamlit as st

# Dynamically handle Google Cloud credentials from Streamlit secrets
credentials_json = st.secrets.get("GOOGLE_APPLICATION_CREDENTIALS")

if credentials_json:
    try:
        # Write credentials to a temporary file
        credentials_path = "/tmp/google_credentials.json"
        with open(credentials_path, "w") as f:
            json.dump(credentials_json, f)
        
        # Set the environment variable to point to the temporary file
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode GOOGLE_APPLICATION_CREDENTIALS: {e}")
else:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not found in Streamlit secrets.")

# Fetch other secrets
instance_id = st.secrets.get('INSTANCE_ID')
database_id = st.secrets.get('DATABASE_ID')
api_key = st.secrets.get('SERP_API_KEY')
openai_api_key = st.secrets.get('OPENAI_API_KEY')
stripe_api_key = st.secrets.get('STRIPE_API_KEY')

# SMTP Configuration for Gmail
smtp_server = "smtp.gmail.com"
smtp_port = 587  # TLS port
smtp_username = "bhaskarabbireddy9@gmail.com"  # Your Gmail address
smtp_password = "ffkv owzp xbvb jbsf"  # App password or Gmail password

# OpenAI API Key
import openai
openai.api_key = openai_api_key
