import stripe
import os 
from src.config import stripe_api_key

# Set your Stripe API keys
stripe.api_key = stripe_api_key # Replace with your Stripe secret key

def create_checkout_session(plan_id, user_email):
    """Create a Stripe Checkout Session for the given plan."""
    try:
        # Map plan details
        plans = {
            "premium_monthly": {"name": "Premium Monthly", "price": 19.99},
            "premium_annual": {"name": "Premium Annual", "price": 199.99},
            "basic_monthly": {"name": "Basic Monthly", "price": 9.99},
            "basic_annual": {"name": "Basic Annual", "price": 99.99},
        }
        plan = plans.get(plan_id)

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
            success_url=f"http://localhost:8501/?success=true&plan_id={plan_id}",
            cancel_url="http://localhost:8501/?canceled=true",
            customer_email=user_email,
        )
        return session.url
    except Exception as e:
        raise RuntimeError(f"Failed to create Stripe Checkout Session: {str(e)}")
