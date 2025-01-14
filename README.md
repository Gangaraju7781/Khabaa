# MarketPlace

## Description

MarketPlace is a Streamlit-based web application that allows users to search for products on Thrive Market, view detailed information about the products, add them to a cart, and generate recipes based on the items in the cart. The application leverages multiple APIs, LLMs and integrates with Google Cloud Spanner for data storage.

## Features

- Search for products on Thrive Market using the SERP API.
- Fetch detailed information about products using web scraping.
- Store product details in a Google Cloud Spanner database.
- Filter products based on user preferences.
- Add products to a cart and generate recipes using OpenAI's GPT-3.

## Project Structure

```
MarketPlace/
│
├── requirements.txt
├── README.md
├── .gitignore
├── config.py
└── src/
    ├── .env
    ├── main.py
    ├── api.py
    ├── spanner_utils.py
    ├── product.py
    └── recipes.py
    └── email_utils.py
    └── handlerss.py
    └── session_manager.py
    └── ui_components.py
```

## Setup

### Prerequisites

- Python 3.7 or higher
- Google Cloud SDK (for Spanner)
- SERP API key
- OpenAI API key

### Installation

1. **Clone the repository:**

   ```bash
   git clone <repository_url>
   cd project_name
   ```

2. **Install the required packages:**

   ```bash
   pip install -r requirements.txt
   ```

3. **Create a `.env` file in the `src` directory and add your API keys:**

   ```txt
   GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/google-credentials.json
   openai_api_key = your_openai_api_key
   api_key = your_serp_api_key
   instance_id = your_spanner_instance_id
   database_id = your_spanner_database_id
   ```

### Usage

1. **Run the Streamlit application:**

   ```bash
   streamlit run src/main.py
   ```

2. **Open the URL provided by Streamlit (e.g., `http://localhost:8501`) in your web browser to use the application.**

## Detailed Explanation

### `config.py`

This file loads environment variables from the `.env` file and sets the Google application credentials for the Spanner.

### `api.py`

This module contains functions to fetch search results from the SERP API and to scrape product details from Thrive Market.

### `spanner_utils.py`

This module contains functions to interact with the Google Cloud Spanner database, including inserting new product data and filtering products based on user preferences.

### `product.py`

This module processes search results, fetches detailed product information, and handles adding products to the cart.

### `recipes.py`

This module generates recipes based on the items in the cart using OpenAI's GPT-3.

### `main.py`

This is the main entry point of the application. It sets up the Streamlit interface, handles user inputs, and coordinates the functionality provided by other modules.

## How It Works

1. **Search Products:**
   - Users enter a search query and specify the number of search results.
   - The application fetches search results using the SERP API and displays product details fetched from Thrive Market.

2. **Filter Products:**
   - Users can specify preferences (gluten-free, vegan, organic) to filter products.
   - The application fetches matching products from the Spanner database based on the preferences.

3. **Add to Cart:**
   - Users can add products to their cart.
   - The application stores the cart items in the session state.

4. **Generate Recipes:**
   - Users can generate recipes based on the items in their cart.
   - The application uses OpenAI's GPT-3 to generate and display recipes.


For any questions or inquiries, please contact gangarajuabbireddy@gmail.com
# Khabaa
# Khabaa
