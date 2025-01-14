import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
import streamlit as st
from src.config import smtp_server, smtp_port, smtp_username, smtp_password
from constants import PLANS

def validate_email(email):
    """Validates the email format."""
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def send_email(recipes, email_address):
    """Sends the generated recipes to the specified email address."""
    try:
        msg = MIMEMultipart()
        msg['From'] = smtp_username
        msg['To'] = email_address
        msg['Subject'] = "Your Generated Recipes from MarketPlace"

        body = "Here are the recipes you generated:\n\n"
        for recipe in recipes:
            body += f"{recipe['name']}\n\n{recipe['details']}\n\n{'-'*40}\n\n"

        msg.attach(MIMEText(body, 'plain'))

        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_username, email_address, text)
        server.quit()

        st.session_state.email_status = "Email sent successfully!"
    except Exception as e:
        st.session_state.email_status = f"Failed to send email: {str(e)}"

def send_subscription_email(plan_name, billing_cycle, user_email):
    """Sends a subscription confirmation email to the user."""
    try:
        # Fetch dynamic benefits for the plan
        plan_benefits = {
            "premium_monthly": [
                "Free delivery",
                "Exclusive recipe generation tools",
                "Priority support",
                "Access to advanced analytics",
            ],
            "premium_annual": [
                "Free delivery",
                "Exclusive recipe generation tools",
                "Priority support",
                "Access to advanced analytics",
            ],
            "basic_monthly": [
                "Discounted delivery for orders over $50",
                "Basic recipe generation tools",
            ],
            "basic_annual": [
                "Discounted delivery for orders over $50",
                "Basic recipe generation tools",
            ],
        }

        # Map the plan to its ID
        plan_id = next(
            (key for key, value in PLANS.items() if value["name"] == plan_name), None
        )
        if not plan_id:
            raise ValueError("Invalid plan name.")

        # Get the benefits for the selected plan
        benefits = plan_benefits.get(plan_id, [])
        formatted_benefits = "\n".join(f"- {benefit}" for benefit in benefits)

        # Construct the email message
        msg = MIMEMultipart()
        msg["From"] = smtp_username
        msg["To"] = user_email
        msg["Subject"] = "Welcome to MarketPlace - Subscription Confirmed"

        # Email body
        body = f"""
        Dear Valued Customer,

        Thank you for subscribing to our {plan_name} ({billing_cycle}) plan!

        We're thrilled to have you as part of the MarketPlace family. Here’s what you’ll enjoy as a subscriber:
        {formatted_benefits}

        If you have any questions, feel free to reach out to us at support@marketplace.com.

        Enjoy your journey with MarketPlace!

        Best Regards,
        The MarketPlace Team
        """

        msg.attach(MIMEText(body, "plain"))

        # Send the email using SMTP
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(smtp_username, smtp_password)
        text = msg.as_string()
        server.sendmail(smtp_username, user_email, text)
        server.quit()

        st.success(f"Subscription confirmation email sent to {user_email}!")
    except Exception as e:
        st.error(f"Failed to send subscription email: {str(e)}")
