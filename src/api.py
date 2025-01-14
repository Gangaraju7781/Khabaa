import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


import requests
import streamlit as st

def fetch_search_results(query, number_of_searches=10, api_key=None):
    """
    Fetches search results from the SERP API for the given query.
    
    Parameters:
    query (str): The Search query.
    number_of_searches (int): Number of Search Results to fetch.

    Returns:
    Dictionary: JSON response from the API.
    
    """
    url = f"https://serpapi.com/search.json?q=site:thrivemarket.com+{query}&engine=google&api_key={api_key}&num={number_of_searches}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching search results: {e}")
        return None
