import os
from dotenv import load_dotenv

import os
import json

# Read from Streamlit secrets
credentials_json = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")

if credentials_json:
    # Write credentials to a temporary file
    credentials_path = "/tmp/google_credentials.json"  # Temp directory for runtime
    with open(credentials_path, "w") as f:
        json.dump(json.loads(credentials_json), f)
    # Set the environment variable to point to the temporary file
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path
else:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not set in environment variables or secrets.")


instance_id = os.getenv('INSTANCE_ID')
database_id = os.getenv('DATABASE_ID')
api_key = os.getenv('SERP_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')
stripe_api_key = os.getenv('STRIPE_API_KEY')

# config.py

# SMTP Configuration for Gmail
smtp_server = "smtp.gmail.com"
smtp_port = 587  # TLS port
smtp_username = "bhaskarabbireddy9@gmail.com"  # Your Gmail address
smtp_password = "ffkv owzp xbvb jbsf"  # App password or Gmail password


import openai
openai.api_key = openai_api_key
