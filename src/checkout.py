import streamlit as st
from datetime import datetime, timedelta
from spanner_utils import fetch_user_subscription, subscribe_user_to_plan
from src.utilss import calculate_cart_total
from payment import create_checkout_session

def checkout_page():
    """Render the Checkout Page."""
    user_id = st.session_state.get("user_id")
    if not user_id:
        st.warning("Please log in to proceed to checkout.")
        return

    st.header("Checkout")

    # Handle Stripe success or failure
    if "success" in st.experimental_get_query_params():
        plan_id = st.experimental_get_query_params().get("plan_id", [None])[0]
        if plan_id:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=30) if "monthly" in plan_id else start_date + timedelta(days=365)
            subscribe_user_to_plan(user_id, plan_id, start_date, end_date)
            st.success(f"Subscription activated: {plan_id.replace('_', ' ').title()}!")
            st.experimental_rerun()

    # Calculate cart total
    cart_total = calculate_cart_total()
    st.write(f"**Cart Total:** ${cart_total:.2f}")

    # Fetch subscription details
    subscription = fetch_user_subscription(user_id)
    if subscription:
        st.write(f"**Subscription Plan:** {subscription[0]}")
        if subscription[0] == "Premium":
            delivery_fee = 0
            st.write("Delivery is free with your Premium plan!")
        elif subscription[0] == "Basic" and cart_total > 50:
            delivery_fee = 0
            st.write("Delivery is free for orders over $50 with your Basic plan!")
        else:
            delivery_fee = 9.99
            st.write("Flat delivery fee applies.")
    else:
        delivery_fee = 9.99
        st.write("Flat delivery fee applies. Upgrade to a subscription for benefits!")

    # Show total cost with delivery
    total_cost = cart_total + delivery_fee
    st.write(f"**Total Cost (Including Delivery):** ${total_cost:.2f}")

    # Payment integration
    if st.button("Proceed to Payment"):
        session_url = create_checkout_session("basic_monthly", st.session_state["email"])
        st.success("Redirecting to payment...")
        st.markdown(f"[Click here to complete your payment]({session_url})")
