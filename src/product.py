import sys
import os

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import requests
from bs4 import BeautifulSoup
import json
import streamlit as st
import uuid
from concurrent.futures import ThreadPoolExecutor

def get_product_details(link):
    """
    Fetch and parse product details from the provided link.

    Args:
        link (str): The URL of the product page.

    Returns:
        dict: A dictionary containing product details such as price, currency, ratings count, 
              product details, product link, description, values, and image URL.
    """
    try:
        product_info = {
            'price': 'N/A',
            'currency': 'N/A',
            'ratings_count': 'N/A',
            'product_details': 'N/A',
            'product_link': 'N/A',
            'description': 'N/A',
            'values': 'N/A',
            'image_url': 'N/A'
        }

        if "thrivemarket.com/p/" in link:
            website_response = requests.get(link)
            if website_response.status_code == 200:
                soup = BeautifulSoup(website_response.text, 'html.parser')
                title = soup.title.text.strip() if soup.title else 'N/A'
                product_info['product_details'] = title.replace('Thrive Market, ', '').replace('| Thrive Market', '')

                json_ld_tag = soup.find('script', {'type': 'application/ld+json'})
                if json_ld_tag:
                    json_ld_content = json.loads(json_ld_tag.string)
                    product_info['description'] = json_ld_content.get('description', 'N/A')
                    offers = json_ld_content.get('offers', {})
                    product_info['price'] = offers.get('price', 'N/A')
                    product_info['currency'] = offers.get('priceCurrency', 'N/A')
                    aggregate_rating = json_ld_content.get('aggregateRating', {})
                    product_info['ratings_count'] = aggregate_rating.get('ratingCount', 'N/A')

                    image_url = json_ld_content.get('image', 'N/A')
                    if isinstance(image_url, list):
                        product_info['image_url'] = image_url[0]
                    else:
                        product_info['image_url'] = image_url

                values_meta_tag = soup.find('meta', {'property': 'sailthru.tags'})
                if values_meta_tag and values_meta_tag.get('content'):
                    values_list = values_meta_tag['content'].split(',')
                    filtered_values = [value.strip() for value in values_list if not value.startswith(('prod', 'product-detail', 'oos-', 'is_grocery', '20-30'))]
                    product_info['values'] = ', '.join(filtered_values) if filtered_values else 'N/A'

                product_info['product_link'] = link
            else:
                st.error(f"Couldn't access {link}, status code {website_response.status_code}")
        else:
            st.error(f"URL didn't match expected pattern: {link}")

        return product_info
    except requests.RequestException as e:
        st.error(f"Error fetching website content for {link}: {e}")
        return product_info
    except json.JSONDecodeError as e:
        st.error(f"Error decoding JSON for {link}: {e}")
        return product_info

def process_search_result(result):
    """
    Process a single search result to extract and display product details.

    Args:
        result (dict): A dictionary containing search result information.

    Returns:
        dict: A dictionary containing processed product information or None if the product details are incomplete.
    """
    link = result.get('link', '')
    product_info = get_product_details(link)
    if product_info['product_details'] != 'N/A' and product_info['price'] != 'N/A':
        price_display = f"{product_info['currency']} {product_info['price']}" if product_info['currency'] != 'N/A' else product_info['price']
        product = {
            "product_id": str(uuid.uuid4()),  # Generate a unique UUID for each product
            "product_details": product_info['product_details'],
            "product_link": product_info['product_link'],
            "price": price_display,
            "number_of_ratings": product_info['ratings_count'],
            "description": product_info['description'],
            "values": product_info['values'],
            "image_url": product_info['image_url']
        }

        st.image(product['image_url'], width=200)
        st.write(f"**{product['product_details']}**")
        st.write(f"Link: [Product Link]({product['product_link']})")
        st.write(f"Price: {product['price']}")
        st.write(f"Number of Ratings: {product['number_of_ratings']}")
        st.write(f"Description: {product['description']}")
        st.write(f"Values: {product['values']}")
        if st.button("Add to Cart", key=product['product_link']):
            if 'cart' not in st.session_state:
                st.session_state.cart = []
            st.session_state.cart.append(product)
            st.success(f"Added {product['product_details']} to cart")
        st.write("************")
        return product
    else:
        st.error("Product details or link missing. Unable to retrieve full information.")
        return None

def parse_search_results(results, expected_count):
    """
    Parse search results to fetch and process product information concurrently.

    Args:
        results (dict): A dictionary containing search results.
        expected_count (int): The number of expected product results.

    Returns:
        list: A list of dictionaries containing fetched product information.
    """
    if results and 'organic_results' in results:
        product_results = [result for result in results['organic_results'] if "thrivemarket.com/p/" in result.get('link', '')]
        fetched_products = []
        with ThreadPoolExecutor(max_workers=5) as executor:
            for product in executor.map(process_search_result, product_results[:expected_count]):
                if product:
                    fetched_products.append(product)

        actual_count = len(fetched_products)
        if actual_count < expected_count:
            st.warning("That's all I could find.")
        return fetched_products

