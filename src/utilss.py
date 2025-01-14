import streamlit as st

def calculate_cart_total():
    cart_items = st.session_state.get('cart', [])
    total = 0
    for item in cart_items:
        price_str = item['price'].replace('USD', '').replace('$', '').replace(',', '').strip()
        total += float(price_str) * item.get('quantity', 1)  # Adjust for quantity
    return total
