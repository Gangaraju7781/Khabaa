import os
from dotenv import load_dotenv

load_dotenv(dotenv_path='src/.env')

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')

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
