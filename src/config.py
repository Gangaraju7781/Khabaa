import os
import json
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv(dotenv_path='src/.env')

# Dynamically handle Google Cloud credentials
credentials_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

if credentials_json:
    try:
        # Write credentials to a temporary file
        credentials_path = "/tmp/google_credentials.json"
        with open(credentials_path, "w") as f:
            json.dump(json.loads(credentials_json), f)
        
        # Set the environment variable to point to the temporary file
        os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to decode GOOGLE_APPLICATION_CREDENTIALS: {e}")
else:
    raise ValueError("GOOGLE_APPLICATION_CREDENTIALS not set in environment variables or secrets.")

# Other environment variables
instance_id = os.getenv('INSTANCE_ID')
database_id = os.getenv('DATABASE_ID')
api_key = os.getenv('SERP_API_KEY')
openai_api_key = os.getenv('OPENAI_API_KEY')
stripe_api_key = os.getenv('STRIPE_API_KEY')

# SMTP Configuration for Gmail
smtp_server = "smtp.gmail.com"
smtp_port = 587  # TLS port
smtp_username = "bhaskarabbireddy9@gmail.com"  # Your Gmail address
smtp_password = "ffkv owzp xbvb jbsf"  # App password or Gmail password

# OpenAI API Key
import openai
openai.api_key = openai_api_key
