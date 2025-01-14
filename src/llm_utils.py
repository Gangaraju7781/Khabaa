# import openai
# import re
# from config import openai_api_key  # Make sure to import your API key from the correct location

# # Initialize the OpenAI client
# client = openai.OpenAI(api_key=openai_api_key)  # Ensure this is consistent with how you initialize elsewhere

# def initialize_llm(api_key):
#     """
#     Initialize the OpenAI client with the provided API key.
#     """
#     global client
#     client = openai.OpenAI(api_key=api_key)
#     return client

# def parse_ingredient_with_llm(client, ingredient):
#     """
#     Use LLM to parse and extract the main ingredient name, ignoring measurements, quantities, and descriptors.

#     Args:
#         client (OpenAI): The OpenAI client instance.
#         ingredient (str): The full ingredient description (e.g., "2 chicken breasts").
    
#     Returns:
#         str: The cleaned ingredient name (e.g., "chicken breast").
#     """
#     # Pre-process ingredient text to remove quantities and measurements
#     cleaned_ingredient = re.sub(r'(\d+\s*)?(cups?|teaspoons?|tablespoons?|ounces?|oz|grams?|ml|liters?|lbs?|pounds?)\s*', '', ingredient, flags=re.IGNORECASE).strip()

#     prompt = f"Extract only the main ingredient name from '{cleaned_ingredient}', ignoring any quantities, measurements, and descriptive words like 'organic', 'fresh', etc."

#     try:
#         # Use the same model and method as in recipe generation
#         response = client.chat.completions.create(
#             model="gpt-3.5-turbo",
#             messages=[
#                 {"role": "system", "content": "You are a helpful assistant that extracts main ingredient names."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=10,
#             temperature=0.2
#         )
#         parsed_ingredient = response.choices[0].message.content.strip().lower()

#         # Further clean up to remove any common descriptors
#         unwanted_descriptors = ["organic", "fresh", "canned", "frozen", "dried", "raw", "boneless", "skinless", "large", "small"]
#         for descriptor in unwanted_descriptors:
#             parsed_ingredient = parsed_ingredient.replace(descriptor, "").strip()

#         print(f"Original ingredient: '{ingredient}', Cleaned ingredient: '{parsed_ingredient}'")

#         return parsed_ingredient
#     except (openai.error.APIConnectionError, openai.error.RateLimitError, openai.error.APIError) as e:
#         print(f"OpenAI API error in LLM parsing: {e}")
#         return ingredient.lower()
#     except Exception as e:
#         print(f"Unexpected error in LLM parsing: {e}")
#         return ingredient.lower()

import openai
import re
from config import openai_api_key  # Make sure to import your API key from the correct location

# Initialize the OpenAI client
client = openai.OpenAI(api_key=openai_api_key)  # Ensure this is consistent with how you initialize elsewhere

def initialize_llm(api_key):
    """
    Initialize the OpenAI client with the provided API key.
    """
    global client
    client = openai.OpenAI(api_key=api_key)
    return client

def parse_ingredient_with_llm(client, ingredient):
    """
    Use LLM to parse and extract the main ingredient name, ignoring measurements, quantities, and descriptors.

    Args:
        client (OpenAI): The OpenAI client instance.
        ingredient (str): The full ingredient description (e.g., "4 cups chicken broth").
    
    Returns:
        str: The cleaned ingredient name (e.g., "chicken broth").
    """
    # Pre-process ingredient text to remove quantities and measurements
    cleaned_ingredient = re.sub(r'(\d+\s*)?(cups?|teaspoons?|tablespoons?|ounces?|oz|grams?|ml|liters?|lbs?|pounds?)\s*', '', ingredient, flags=re.IGNORECASE).strip()

    # Refine prompt for specificity
    prompt = f"Extract the main ingredient name from '{cleaned_ingredient}', keeping specific details like 'broth', 'powder', 'stock', etc., but ignoring numbers, quantities, and adjectives like 'organic' or 'fresh'. Only return the most relevant ingredient term."

    try:
        # Use the same model and method as in recipe generation
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that extracts main ingredient names."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=10,
            temperature=0.2
        )
        parsed_ingredient = response.choices[0].message.content.strip().lower()

        # Further cleaning to remove common descriptors
        unwanted_descriptors = ["organic", "fresh", "canned", "frozen", "dried", "raw", "boneless", "skinless", "large", "small"]
        for descriptor in unwanted_descriptors:
            parsed_ingredient = parsed_ingredient.replace(descriptor, "").strip()

        # Additional checks for more specific matches
        specific_terms = ["broth", "stock", "powder", "cream", "flour", "butter", "oil", "paste", "sauce"]
        for term in specific_terms:
            if term in cleaned_ingredient.lower() and term not in parsed_ingredient:
                parsed_ingredient += f" {term}"

        print(f"Original ingredient: '{ingredient}', Cleaned ingredient: '{parsed_ingredient}'")

        return parsed_ingredient.strip()
    except (openai.error.APIConnectionError, openai.error.RateLimitError, openai.error.APIError) as e:
        print(f"OpenAI API error in LLM parsing: {e}")
        return ingredient.lower()
    except Exception as e:
        print(f"Unexpected error in LLM parsing: {e}")
        return ingredient.lower()
