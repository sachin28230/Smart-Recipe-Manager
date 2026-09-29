from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_recommendations(recipes, selected_recipe_id, number_of_recommendations=5):

    if not recipes:
        return []

    recipe_texts = []

    for recipe in recipes:

        # Give ingredients more importance
        ingredients = recipe.ingredients or ""

        # Repeat ingredients to give them higher weight
        weighted_ingredients = (
            ingredients + " " +
            ingredients + " " +
            ingredients
        )

        text = " ".join([
            recipe.name or "",
            recipe.description or "",
            weighted_ingredients,
            recipe.nutrition_tips or ""
        ])

        recipe_texts.append(text.lower())

    # Convert recipe information into TF-IDF vectors
    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(recipe_texts)

    # Find selected recipe
    selected_index = None

    for index, recipe in enumerate(recipes):

        if recipe.id == selected_recipe_id:
            selected_index = index
            break

    if selected_index is None:
        return []

    # Calculate cosine similarity
    similarity_scores = cosine_similarity(
        tfidf_matrix[selected_index:selected_index + 1],
        tfidf_matrix
    )[0]

    recipe_scores = []

    for index, score in enumerate(similarity_scores):

        # Don't recommend the same recipe
        if recipes[index].id == selected_recipe_id:
            continue

        recipe_scores.append(
            (recipes[index], score)
        )

    # Sort by similarity
    recipe_scores.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return recipe_scores[:number_of_recommendations]
def get_ingredient_ml_scores(recipes, ingredients_input):

    if not recipes or not ingredients_input:
        return {}

    # Create text for the user's ingredients
    user_text = ingredients_input.lower()

    recipe_texts = []

    for recipe in recipes:

        # Give ingredients more importance
        ingredients = recipe.ingredients or ""

        weighted_ingredients = (
            ingredients + " " +
            ingredients + " " +
            ingredients
        )

        recipe_text = " ".join([
            recipe.name or "",
            weighted_ingredients,
            recipe.description or ""
        ])

        recipe_texts.append(recipe_text.lower())

    # Combine user's ingredients with all recipe text
    all_texts = [user_text] + recipe_texts

    # Convert text into TF-IDF vectors
    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # Compare user's ingredients with every recipe
    similarity_scores = cosine_similarity(
        tfidf_matrix[0:1],
        tfidf_matrix[1:]
    )[0]

    # Store score using recipe ID
    scores = {}

    for index, recipe in enumerate(recipes):

        scores[recipe.id] = similarity_scores[index]

    return scores
def get_personalized_recommendations(
    recipes,
    favorite_recipe_ids,
    number_of_recommendations=5
):

    if not recipes or not favorite_recipe_ids:
        return []

    recipe_texts = []

    for recipe in recipes:

        ingredients = recipe.ingredients or ""

        # Give ingredients higher importance
        weighted_ingredients = (
            ingredients + " " +
            ingredients + " " +
            ingredients
        )

        text = " ".join([
            recipe.name or "",
            recipe.description or "",
            weighted_ingredients,
            recipe.nutrition_tips or ""
        ])

        recipe_texts.append(text.lower())

    # Convert recipes into TF-IDF vectors
    vectorizer = TfidfVectorizer(
        stop_words="english"
    )

    tfidf_matrix = vectorizer.fit_transform(recipe_texts)

    # Find indexes of user's favorite recipes
    favorite_indexes = []

    for index, recipe in enumerate(recipes):

        if recipe.id in favorite_recipe_ids:
            favorite_indexes.append(index)

    if not favorite_indexes:
        return []

    # Calculate similarity between all recipes
    similarity_matrix = cosine_similarity(
        tfidf_matrix,
        tfidf_matrix
    )

    recommendation_scores = []

    for index, recipe in enumerate(recipes):

        # Don't recommend recipes already favorited
        if recipe.id in favorite_recipe_ids:
            continue

        # Find similarity to each favorite recipe
        favorite_scores = []

        for favorite_index in favorite_indexes:

            favorite_scores.append(
                similarity_matrix[index][favorite_index]
            )

        # Use the highest similarity to a favorite
        if favorite_scores:

            best_score = max(favorite_scores)

            recommendation_scores.append(
                (recipe, best_score)
            )

    # Highest similarity first
    recommendation_scores.sort(
        key=lambda x: x[1],
        reverse=True
    )

    return recommendation_scores[
        :number_of_recommendations
    ]