# import streamlit as st
# import stripe
# from datetime import datetime, timedelta
# from spanner_utils import subscribe_user_to_plan, fetch_user_subscription
# from email_utils import send_subscription_email
# from constants import PLANS

# # Set your Stripe API keys
# stripe.api_key = "your_stripe_secret_key"  # Replace with your Stripe secret key


# def create_checkout_session(plan_id, user_email):
#     """Create a Stripe Checkout Session for the given plan."""
#     try:
#         plan = PLANS.get(plan_id)
#         if not plan:
#             raise ValueError("Invalid plan ID")

#         # Create Stripe Checkout Session
#         session = stripe.checkout.Session.create(
#             payment_method_types=["card"],
#             line_items=[
#                 {
#                     "price_data": {
#                         "currency": "usd",
#                         "product_data": {"name": plan["name"]},
#                         "unit_amount": int(plan["price"] * 100),  # Stripe expects amount in cents
#                     },
#                     "quantity": 1,
#                 }
#             ],
#             mode="payment",
#             success_url=f"http://localhost:8501/subscriptions?success=true&plan_id={plan_id}",
#             cancel_url="http://localhost:8501/subscriptions?canceled=true",
#             customer_email=user_email,
#         )
#         return session.url
#     except Exception as e:
#         raise RuntimeError(f"Failed to create Stripe Checkout Session: {str(e)}")

# def subscription_page():
#     """Render the Subscriptions Page."""
#     user_id = st.session_state.get("user_id")
#     user_email = st.session_state.get("email")

#     if not user_id:
#         st.warning("Please log in to manage your subscription.")
#         return

#     st.header("Your Subscription")

#     # Handle Payment Success
#     if "success" in st.experimental_get_query_params():
#         plan_id = st.experimental_get_query_params().get("plan_id", [None])[0]
#         if plan_id:
#             start_date = datetime.now()
#             end_date = start_date + timedelta(days=30) if "monthly" in plan_id else start_date + timedelta(days=365)
#             subscribe_user_to_plan(user_id, plan_id, start_date, end_date)

#             # Fetch plan details
#             plan_details = PLANS.get(plan_id)
#             if plan_details:
#                 plan_name = plan_details['name']
#                 billing_cycle = "Monthly" if "monthly" in plan_id else "Annual"

#                 # Send subscription email
#                 send_subscription_email(plan_name, billing_cycle, user_email)

#             st.success(f"Subscription activated for {plan_name}!")
#             st.experimental_rerun()

#     # Fetch current subscription
#     current_subscription = fetch_user_subscription(user_id)
#     if current_subscription:
#         st.subheader("Current Plan")
#         st.write(f"**Plan Name:** {current_subscription[0]}")
#         st.write(f"**Billing Cycle:** {current_subscription[1]}")
#         st.write(f"**Cost:** ${current_subscription[2]:.2f}")
#         st.write(f"**Benefits:** {current_subscription[3]}")
#     else:
#         st.info("You currently have no active subscription.")

#     # Display available plans
#     st.subheader("Available Plans")
#     for plan_id, plan in PLANS.items():
#         st.write(f"**{plan['name']}** - ${plan['price']:.2f}")
#         if st.button(f"Subscribe to {plan['name']}", key=plan_id):
#             if user_email:
#                 session_url = create_checkout_session(plan_id, user_email)
#                 st.success("Redirecting to payment...")
#                 st.markdown(f"[Click here to complete your payment]({session_url})")
#             else:
#                 st.warning("Email address is required for payment.")


import streamlit as st
import stripe
from datetime import datetime, timedelta
from spanner_utils import subscribe_user_to_plan, fetch_user_subscription
from email_utils import send_subscription_email
from constants import PLANS
from src.config import stripe_api_key

# Set your Stripe API keys
stripe.api_key = stripe_api_key  # Replace with your Stripe secret key


def create_checkout_session(plan_id, user_email):
    """Create a Stripe Checkout Session for the given plan."""
    try:
        plan = PLANS.get(plan_id)
        if not plan:
            raise ValueError("Invalid plan ID")

        # Create Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "usd",
                        "product_data": {"name": plan["name"]},
                        "unit_amount": int(plan["price"] * 100),  # Stripe expects amount in cents
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url=f"http://localhost:8501/subscriptions?success=true&plan_id={plan_id}",
            cancel_url="http://localhost:8501/subscriptions?canceled=true",
            customer_email=user_email,
        )
        return session.url
    except Exception as e:
        raise RuntimeError(f"Failed to create Stripe Checkout Session: {str(e)}")


def subscription_page():
    """Render the Subscriptions Page."""
    user_id = st.session_state.get("user_id")
    user_email = st.session_state.get("email")

    if not user_id:
        st.warning("Please log in to manage your subscription.")
        return

    st.header("Your Subscription")

    # Input email if not already set in the session state
    if not user_email:
        st.warning("Email address is required to proceed with payment.")
        user_email_input = st.text_input("Enter your email address:")
        if st.button("Save Email"):
            if user_email_input:
                st.session_state["email"] = user_email_input
                st.success("Email saved successfully!")
                st.experimental_rerun()
            else:
                st.warning("Please enter a valid email address.")
        return  # Stop rendering the rest of the page until the email is provided

    # Handle Payment Success
    if "success" in st.experimental_get_query_params():
        plan_id = st.experimental_get_query_params().get("plan_id", [None])[0]
        if plan_id:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=30) if "monthly" in plan_id else start_date + timedelta(days=365)
            subscribe_user_to_plan(user_id, plan_id, start_date, end_date)

            # Fetch plan details
            plan_details = PLANS.get(plan_id)
            if plan_details:
                plan_name = plan_details['name']
                billing_cycle = "Monthly" if "monthly" in plan_id else "Annual"

                # Send subscription email
                send_subscription_email(plan_name, billing_cycle, user_email)

            st.success(f"Subscription activated for {plan_name}!")
            st.experimental_rerun()

    # Fetch current subscription
    current_subscription = fetch_user_subscription(user_id)
    if current_subscription:
        st.subheader("Current Plan")
        st.write(f"**Plan Name:** {current_subscription[0]}")
        st.write(f"**Billing Cycle:** {current_subscription[1]}")
        st.write(f"**Cost:** ${current_subscription[2]:.2f}")
        st.write(f"**Benefits:** {current_subscription[3]}")
    else:
        st.info("You currently have no active subscription.")

    # Display available plans
    st.subheader("Available Plans")
    for plan_id, plan in PLANS.items():
        st.write(f"**{plan['name']}** - ${plan['price']:.2f}")
        if st.button(f"Subscribe to {plan['name']}", key=plan_id):
            if user_email:
                session_url = create_checkout_session(plan_id, user_email)
                st.success("Redirecting to payment...")
                st.markdown(f"[Click here to complete your payment]({session_url})")
            else:
                st.warning("Email address is required for payment.")
