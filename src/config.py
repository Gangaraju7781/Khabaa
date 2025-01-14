import os
import json
import streamlit as st

# Fetch credentials from Streamlit secrets
credentials_json = st.secrets["GOOGLE_APPLICATION_CREDENTIALS"]

if credentials_json:
    try:
        # Convert AttrDict to a plain dictionary
        credentials_dict = dict(credentials_json)

        # Write credentials to a temporary file
        credentials_path = "/tmp/google_credentials.json"
        with open(credentials_path, "w") as f:
            json.dump(credentials_dict, f)
        
        # Set the environment variable to point to the temporary file
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode GOOGLE_APPLICATION_CREDENTIALS: {e}")
else:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not found in Streamlit secrets.")

# Fetch other secrets and convert to strings
instance_id = st.secrets['INSTANCE_ID']
database_id = st.secrets['DATABASE_ID']
api_key = st.secrets['SERP_API_KEY']
openai_api_key = st.secrets['OPENAI_API_KEY']
stripe_api_key = st.secrets['STRIPE_API_KEY']

# SMTP Configuration for Gmail
smtp_server = "smtp.gmail.com"
smtp_port = 587  # TLS port
smtp_username = "bhaskarabbireddy9@gmail.com"  # Your Gmail address
smtp_password = "ffkv owzp xbvb jbsf"  # App password or Gmail password

# OpenAI API Key
import openai
openai.api_key = openai_api_key
