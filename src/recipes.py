import openai
import re
import random
from config import openai_api_key

# Initialize the OpenAI client
client = openai.OpenAI(api_key=openai_api_key)

def extract_cooking_time(response_text):
    """
    Extracts cooking time from OpenAI response using regex.
    Returns the maximum value of the cooking time in minutes.
    If no cooking time is mentioned, return None to use the user's max time.
    """
    match = re.search(r'(\d+)(?:-(\d+))?\s*(minutes|min)', response_text, re.IGNORECASE)
    if match:
        min_time = int(match.group(1))
        max_time = int(match.group(2)) if match.group(2) else min_time
        return max(max_time, min_time)
    else:
        return None

def clean_recipe_title(recipe_text):
    """
    Cleans up the recipe title to remove unnecessary prefixes and introduction texts.
    It returns the proper recipe name.
    """
    cleaned_title = re.sub(r'(Recipe:|Recipe for Day \d+:|Here is a simple and flavorful recipe using .*:)', '', recipe_text).strip()
    return cleaned_title

def format_total_cooking_time(cooking_time):
    """
    Formats the total cooking time into a consistent format.
    """
    return f"**Total Cooking Time: {cooking_time} minutes**"

def extract_missing_ingredients(response_text):
    """
    Extracts missing ingredients from the response text.
    """
    start_idx = response_text.find('Ingredients Missing:')
    if start_idx != -1:
        missing_ingredients_section = response_text[start_idx + len('Ingredients Missing:'):].split('\n')
        return [ingredient.strip() for ingredient in missing_ingredients_section if ingredient.strip()]
    return []

def generate_recipes(cart_items, recipe_name=None, min_time=0, max_time=0):
    """
    Generate or check recipes based on the provided ingredients.
    If a `recipe_name` is provided, the function checks if the recipe can be 
    made with the ingredients in `cart_items`, lists any missing ingredients, 
    and generates the complete recipe. If no `recipe_name` is provided, it 
    generates recipes using the available ingredients.
    """
    if not cart_items:
        ingredients = []
        cart_section = "No ingredients in your cart."
    else:
        ingredients = [item['product_details'] for item in cart_items]
        cart_section = f"Ingredients in Your Cart:\n- " + "\n- ".join(ingredients)
    
    if recipe_name:
        # If a recipe name is provided, check for missing ingredients and generate the recipe
        if not ingredients:
            ingredients_placeholder = "None"
        else:
            ingredients_placeholder = ', '.join(ingredients)
            
        prompt = f"Check if the following recipe '{recipe_name}' can be made with these ingredients: {ingredients_placeholder}. Ingredients Missing are ingredients needed for the recipe that are not already added to the cart. {cart_section}. First display ingredients in your cart (with measurements), then ingredients missing (with measurements), then the instructions. Make the section labels like ingredients and instructions bolded."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that checks for missing ingredients and generates recipes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500  # Adjust as necessary
        )

        recipe_details = response.choices[0].message.content.strip()
        return [{"name": recipe_name, "details": recipe_details}]
    
    else:
        if not ingredients:
            return [{"name": "No Recipes", "details": "Please add ingredients to your cart to generate recipes."}]
        
        prompt = f"Generate recipes using some or all of the following ingredients: {', '.join(ingredients)}. Ensure the total cooking time falls between {min_time} and {max_time} minutes."
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates recipes."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=1000
        )
        
        recipes_text = response.choices[0].message.content.strip()
        recipes = recipes_text.split('\n\nRecipe ')
        formatted_recipes = []

        for i, recipe in enumerate(recipes):
            total_cooking_time = extract_cooking_time(recipe) or max_time
            if min_time <= total_cooking_time <= max_time + 5:
                first_ingredient = recipe.splitlines()[1]  
                recipe_dict = {
                    "name": f"Meal {i + 1}: {clean_recipe_title(first_ingredient)}",
                    "details": f"{recipe.strip()}\n\n{format_total_cooking_time(total_cooking_time)}"
                }
                formatted_recipes.append(recipe_dict)
        
        return formatted_recipes

def generate_weekly_meal_plan(cart_items, selected_cuisines, min_time=0, max_time=0, num_days=7):
    """
    Generate a weekly meal plan with missing ingredients listed for each recipe.
    Each recipe will use different cooking techniques, flavor profiles, and cuisines.
    Ensure consistency in title and total cooking time display.
    """
    if not cart_items:
        ingredients = []
    else:
        ingredients = [item['product_details'] for item in cart_items]

    meal_plan = []
    cooking_methods = ["grilled", "roasted", "baked", "steamed", "poached", "sautéed", "stir-fried"]

    # Use default cuisines if no selection is made
    if not selected_cuisines:
        selected_cuisines = ["Italian", "Indian", "Mexican", "Mediterranean", "Thai", "Japanese", "American"]

    # Shuffle the ingredients for variety
    random.shuffle(ingredients)

    # Generate one recipe at a time until 7 recipes are generated
    for idx in range(num_days):
        cuisine = selected_cuisines[idx % len(selected_cuisines)]  # Ensure cuisine rotation
        method = cooking_methods[idx % len(cooking_methods)]       # Rotate cooking methods

        # If only 1 ingredient, use it across all recipes with different methods
        if len(ingredients) == 1:
            selected_ingredients = ingredients
        else:
            # For each recipe, pick a random subset of ingredients (between 1 and 3)
            num_ingredients = random.randint(1, min(3, len(ingredients)))
            selected_ingredients = random.sample(ingredients, num_ingredients)

        # Prompt for OpenAI to generate recipe
        prompt = f"Create a unique {cuisine} recipe using {method} with the following ingredients: {', '.join(selected_ingredients)}. List the ingredients, highlight any missing ingredients, and provide instructions. Ensure the total cooking time falls between {min_time} and {max_time} minutes."

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates meal plans and identifies missing ingredients with varied culinary styles."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )

        recipe_text = response.choices[0].message.content.strip()
        recipe_lines = recipe_text.splitlines()

        # Add a check to prevent accessing an out-of-range index
        if len(recipe_lines) > 1:
            recipe_title = clean_recipe_title(recipe_lines[1])
        else:
            recipe_title = "Recipe Title Not Available"

        missing_ingredients = extract_missing_ingredients(recipe_text)
        total_cooking_time = extract_cooking_time(recipe_text) or max_time

        if min_time <= total_cooking_time <= max_time + 5:
            meal_plan.append({
                "name": f"Meal {len(meal_plan) + 1}: {recipe_title}",
                "details": f"{recipe_text}\n\n{format_total_cooking_time(total_cooking_time)}",
                "missing_ingredients": missing_ingredients
            })
        
        # Stop once we have exactly 7 recipes
        if len(meal_plan) >= num_days:
            break

    return meal_plan