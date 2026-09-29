from app import app, db, Recipe


recipes = [

    {
        "name": "Idli",
        "description": "Soft and steamed South Indian rice cakes.",
        "ingredients": "Rice, Urad Dal, Salt, Water",
        "instructions": "1. Soak rice and urad dal. 2. Grind them into batter. 3. Ferment the batter. 4. Pour into idli moulds. 5. Steam until cooked.",
        "cooking_time": 30,
        "calories": 170,
        "protein": 6,
        "carbohydrates": 35,
        "fat": 1
    },

    {
        "name": "Medu Vada",
        "description": "Crispy South Indian lentil fritters.",
        "ingredients": "Urad Dal, Onion, Green Chilli, Ginger, Salt, Oil",
        "instructions": "1. Soak urad dal. 2. Grind into a thick batter. 3. Add onion, chilli and ginger. 4. Shape into vadas. 5. Deep fry until golden.",
        "cooking_time": 35,
        "calories": 280,
        "protein": 8,
        "carbohydrates": 30,
        "fat": 14
    },

    {
        "name": "Vegetable Upma",
        "description": "Healthy South Indian breakfast made with semolina and vegetables.",
        "ingredients": "Rava, Onion, Carrot, Beans, Green Chilli, Mustard Seeds, Salt, Oil",
        "instructions": "1. Roast rava. 2. Fry mustard seeds and vegetables. 3. Add water and salt. 4. Slowly add rava. 5. Cook until soft.",
        "cooking_time": 25,
        "calories": 250,
        "protein": 7,
        "carbohydrates": 40,
        "fat": 8
    },

    {
        "name": "Lemon Rice",
        "description": "Tangy rice dish flavored with lemon and spices.",
        "ingredients": "Cooked Rice, Lemon, Peanut, Green Chilli, Mustard Seeds, Turmeric, Salt, Oil",
        "instructions": "1. Heat oil. 2. Add mustard seeds and peanuts. 3. Add chilli and turmeric. 4. Add cooked rice. 5. Add lemon juice and mix.",
        "cooking_time": 20,
        "calories": 320,
        "protein": 7,
        "carbohydrates": 55,
        "fat": 9
    },

    {
        "name": "Curd Rice",
        "description": "Simple and refreshing rice mixed with curd and seasoning.",
        "ingredients": "Cooked Rice, Curd, Milk, Green Chilli, Ginger, Mustard Seeds, Salt, Oil",
        "instructions": "1. Mash cooked rice. 2. Add curd and milk. 3. Prepare seasoning. 4. Mix everything together. 5. Serve chilled or at room temperature.",
        "cooking_time": 15,
        "calories": 260,
        "protein": 8,
        "carbohydrates": 42,
        "fat": 6
    },

    {
        "name": "Vegetable Pulao",
        "description": "Aromatic rice cooked with mixed vegetables and spices.",
        "ingredients": "Basmati Rice, Carrot, Beans, Peas, Onion, Tomato, Green Chilli, Garam Masala, Salt, Oil",
        "instructions": "1. Fry onion and spices. 2. Add vegetables. 3. Add rice. 4. Add water and salt. 5. Cook until rice is tender.",
        "cooking_time": 35,
        "calories": 390,
        "protein": 9,
        "carbohydrates": 65,
        "fat": 10
    },

    {
        "name": "Sambar",
        "description": "South Indian lentil and vegetable curry.",
        "ingredients": "Toor Dal, Tomato, Onion, Carrot, Potato, Drumstick, Tamarind, Sambar Powder, Salt",
        "instructions": "1. Cook toor dal. 2. Cook vegetables. 3. Add tamarind and sambar powder. 4. Add cooked dal. 5. Simmer and serve.",
        "cooking_time": 40,
        "calories": 180,
        "protein": 9,
        "carbohydrates": 25,
        "fat": 5
    },

    {
        "name": "Palak Paneer",
        "description": "Paneer cooked in a creamy spinach gravy.",
        "ingredients": "Paneer, Spinach, Onion, Tomato, Ginger, Garlic, Cream, Garam Masala, Salt, Oil",
        "instructions": "1. Blanch spinach. 2. Make spinach puree. 3. Prepare onion tomato gravy. 4. Add spinach puree. 5. Add paneer and spices.",
        "cooking_time": 35,
        "calories": 390,
        "protein": 19,
        "carbohydrates": 14,
        "fat": 28
    },

    {
        "name": "Chole Masala",
        "description": "Spicy chickpea curry prepared with Indian spices.",
        "ingredients": "Chickpeas, Onion, Tomato, Ginger, Garlic, Green Chilli, Chole Masala, Salt, Oil",
        "instructions": "1. Soak chickpeas overnight. 2. Pressure cook chickpeas. 3. Prepare onion tomato gravy. 4. Add spices. 5. Add chickpeas and simmer.",
        "cooking_time": 45,
        "calories": 330,
        "protein": 15,
        "carbohydrates": 45,
        "fat": 10
    },

    {
        "name": "Rajma Masala",
        "description": "Kidney beans cooked in a rich tomato gravy.",
        "ingredients": "Rajma, Onion, Tomato, Ginger, Garlic, Garam Masala, Chilli Powder, Salt, Oil",
        "instructions": "1. Soak rajma overnight. 2. Pressure cook rajma. 3. Prepare onion tomato gravy. 4. Add spices. 5. Add rajma and simmer.",
        "cooking_time": 50,
        "calories": 340,
        "protein": 16,
        "carbohydrates": 48,
        "fat": 9
    },

    {
        "name": "Aloo Paratha",
        "description": "Indian flatbread stuffed with spiced potato.",
        "ingredients": "Wheat Flour, Potato, Onion, Green Chilli, Coriander, Cumin, Salt, Oil",
        "instructions": "1. Prepare wheat dough. 2. Boil and mash potatoes. 3. Mix potato with spices. 4. Stuff dough. 5. Roll and cook on a hot pan.",
        "cooking_time": 35,
        "calories": 300,
        "protein": 7,
        "carbohydrates": 45,
        "fat": 10
    },

    {
        "name": "Poori Masala",
        "description": "Crispy fried bread served with potato masala.",
        "ingredients": "Wheat Flour, Potato, Onion, Green Chilli, Mustard Seeds, Turmeric, Salt, Oil",
        "instructions": "1. Prepare wheat dough. 2. Make potato masala. 3. Roll small pooris. 4. Deep fry. 5. Serve with potato masala.",
        "cooking_time": 35,
        "calories": 380,
        "protein": 8,
        "carbohydrates": 52,
        "fat": 16
    },

    {
        "name": "Egg Curry",
        "description": "Boiled eggs cooked in a spicy onion tomato gravy.",
        "ingredients": "Egg, Onion, Tomato, Ginger, Garlic, Green Chilli, Garam Masala, Turmeric, Salt, Oil",
        "instructions": "1. Boil eggs. 2. Prepare onion tomato gravy. 3. Add spices. 4. Add boiled eggs. 5. Simmer for a few minutes.",
        "cooking_time": 30,
        "calories": 290,
        "protein": 18,
        "carbohydrates": 12,
        "fat": 18
    },

    {
        "name": "Chicken Curry",
        "description": "Traditional Indian chicken curry with aromatic spices.",
        "ingredients": "Chicken, Onion, Tomato, Ginger, Garlic, Green Chilli, Garam Masala, Turmeric, Salt, Oil",
        "instructions": "1. Marinate chicken. 2. Fry onion. 3. Add ginger and garlic. 4. Add tomato and spices. 5. Add chicken and cook until tender.",
        "cooking_time": 50,
        "calories": 450,
        "protein": 38,
        "carbohydrates": 12,
        "fat": 26
    },

    {
        "name": "Chicken Fried Rice",
        "description": "Fried rice prepared with chicken and vegetables.",
        "ingredients": "Cooked Rice, Chicken, Carrot, Beans, Capsicum, Spring Onion, Soy Sauce, Pepper, Salt, Oil",
        "instructions": "1. Cook chicken. 2. Stir-fry vegetables. 3. Add chicken. 4. Add cooked rice. 5. Add soy sauce and seasoning.",
        "cooking_time": 30,
        "calories": 520,
        "protein": 28,
        "carbohydrates": 65,
        "fat": 16
    },

    {
        "name": "Vegetable Pasta",
        "description": "Pasta cooked with vegetables in a tomato sauce.",
        "ingredients": "Pasta, Tomato, Onion, Carrot, Capsicum, Garlic, Chilli Flakes, Salt, Oil",
        "instructions": "1. Boil pasta. 2. Prepare tomato sauce. 3. Saute vegetables. 4. Add pasta. 5. Mix and serve.",
        "cooking_time": 30,
        "calories": 390,
        "protein": 12,
        "carbohydrates": 62,
        "fat": 11
    },

    {
        "name": "Tomato Soup",
        "description": "Warm and comforting soup made from fresh tomatoes.",
        "ingredients": "Tomato, Onion, Garlic, Pepper, Butter, Salt, Water",
        "instructions": "1. Cook tomatoes and onion. 2. Blend into puree. 3. Add water. 4. Add pepper and salt. 5. Simmer and serve.",
        "cooking_time": 25,
        "calories": 150,
        "protein": 4,
        "carbohydrates": 18,
        "fat": 7
    },

    {
        "name": "Mixed Vegetable Curry",
        "description": "Mixed vegetables cooked in a flavorful Indian gravy.",
        "ingredients": "Carrot, Beans, Potato, Peas, Capsicum, Onion, Tomato, Ginger, Garlic, Garam Masala, Salt, Oil",
        "instructions": "1. Chop vegetables. 2. Prepare onion tomato gravy. 3. Add spices. 4. Add vegetables. 5. Cook until tender.",
        "cooking_time": 40,
        "calories": 260,
        "protein": 8,
        "carbohydrates": 30,
        "fat": 12
    },

    {
        "name": "Aloo Gobi",
        "description": "Classic Indian potato and cauliflower curry.",
        "ingredients": "Potato, Cauliflower, Onion, Tomato, Green Chilli, Turmeric, Garam Masala, Salt, Oil",
        "instructions": "1. Cut potato and cauliflower. 2. Fry onion. 3. Add tomato and spices. 4. Add vegetables. 5. Cook until tender.",
        "cooking_time": 35,
        "calories": 230,
        "protein": 6,
        "carbohydrates": 32,
        "fat": 9
    },

    {
        "name": "Dal Tadka",
        "description": "Yellow lentils finished with a fragrant spice tempering.",
        "ingredients": "Toor Dal, Onion, Tomato, Garlic, Green Chilli, Cumin, Turmeric, Salt, Ghee",
        "instructions": "1. Cook dal. 2. Prepare onion tomato mixture. 3. Add cooked dal. 4. Prepare garlic cumin tempering. 5. Add tempering to dal.",
        "cooking_time": 35,
        "calories": 240,
        "protein": 12,
        "carbohydrates": 32,
        "fat": 8
    },

    {
        "name": "Veg Manchurian",
        "description": "Crispy vegetable balls served with Indo-Chinese sauce.",
        "ingredients": "Cabbage, Carrot, Capsicum, Corn Flour, Onion, Garlic, Soy Sauce, Pepper, Salt, Oil",
        "instructions": "1. Mix vegetables with flour. 2. Shape into balls. 3. Fry until crispy. 4. Prepare sauce. 5. Add fried balls to sauce.",
        "cooking_time": 40,
        "calories": 360,
        "protein": 8,
        "carbohydrates": 42,
        "fat": 17
    },

    {
        "name": "Masala Omelette",
        "description": "Egg omelette packed with onion, tomato and green chilli.",
        "ingredients": "Egg, Onion, Tomato, Green Chilli, Coriander, Pepper, Salt, Oil",
        "instructions": "1. Beat eggs. 2. Add chopped vegetables and seasoning. 3. Heat pan. 4. Pour egg mixture. 5. Cook both sides.",
        "cooking_time": 10,
        "calories": 210,
        "protein": 14,
        "carbohydrates": 5,
        "fat": 15
    },

    {
        "name": "Vegetable Sandwich",
        "description": "Quick sandwich filled with fresh vegetables.",
        "ingredients": "Bread, Potato, Tomato, Onion, Capsicum, Cucumber, Butter, Salt, Pepper",
        "instructions": "1. Slice vegetables. 2. Season vegetables. 3. Spread butter on bread. 4. Add vegetables. 5. Toast and serve.",
        "cooking_time": 15,
        "calories": 280,
        "protein": 8,
        "carbohydrates": 38,
        "fat": 10
    },

    {
        "name": "Poha",
        "description": "Light Indian breakfast made with flattened rice.",
        "ingredients": "Poha, Onion, Potato, Peanuts, Green Chilli, Mustard Seeds, Turmeric, Lemon, Salt, Oil",
        "instructions": "1. Wash poha. 2. Fry mustard seeds and peanuts. 3. Add onion and potato. 4. Add poha and turmeric. 5. Finish with lemon juice.",
        "cooking_time": 20,
        "calories": 270,
        "protein": 7,
        "carbohydrates": 42,
        "fat": 8
    },

    {
        "name": "Veg Biryani",
        "description": "Fragrant basmati rice cooked with vegetables and spices.",
        "ingredients": "Basmati Rice, Carrot, Beans, Peas, Potato, Onion, Tomato, Yogurt, Biryani Masala, Salt, Oil",
        "instructions": "1. Prepare vegetables. 2. Cook rice partially. 3. Prepare vegetable masala. 4. Layer rice and vegetables. 5. Cook on low heat.",
        "cooking_time": 55,
        "calories": 480,
        "protein": 10,
        "carbohydrates": 72,
        "fat": 15
    },

    {
        "name": "Matar Paneer",
        "description": "Paneer and green peas cooked in tomato gravy.",
        "ingredients": "Paneer, Peas, Onion, Tomato, Ginger, Garlic, Garam Masala, Turmeric, Salt, Oil",
        "instructions": "1. Prepare tomato onion gravy. 2. Add spices. 3. Add peas. 4. Add paneer. 5. Simmer until cooked.",
        "cooking_time": 35,
        "calories": 380,
        "protein": 18,
        "carbohydrates": 18,
        "fat": 25
    },

    {
        "name": "Pav Bhaji",
        "description": "Spiced mashed vegetable curry served with toasted pav.",
        "ingredients": "Potato, Tomato, Onion, Capsicum, Peas, Cauliflower, Pav Bhaji Masala, Butter, Salt",
        "instructions": "1. Boil vegetables. 2. Mash vegetables. 3. Fry onion and tomato. 4. Add vegetables and masala. 5. Cook and serve with toasted pav.",
        "cooking_time": 40,
        "calories": 420,
        "protein": 10,
        "carbohydrates": 58,
        "fat": 16
    },

    {
        "name": "Dahi Vada",
        "description": "Soft lentil dumplings served with seasoned yogurt.",
        "ingredients": "Urad Dal, Curd, Green Chilli, Ginger, Cumin, Chaat Masala, Salt, Oil",
        "instructions": "1. Soak and grind urad dal. 2. Make vadas. 3. Fry until golden. 4. Soak in water. 5. Serve with seasoned curd.",
        "cooking_time": 45,
        "calories": 300,
        "protein": 10,
        "carbohydrates": 32,
        "fat": 13
    },

    {
        "name": "Mushroom Masala",
        "description": "Mushrooms cooked in an aromatic onion tomato gravy.",
        "ingredients": "Mushroom, Onion, Tomato, Ginger, Garlic, Green Chilli, Garam Masala, Turmeric, Salt, Oil",
        "instructions": "1. Clean mushrooms. 2. Fry onion. 3. Add ginger and garlic. 4. Add tomato and spices. 5. Add mushrooms and cook.",
        "cooking_time": 30,
        "calories": 220,
        "protein": 9,
        "carbohydrates": 15,
        "fat": 13
    },

    {
        "name": "Coconut Rice",
        "description": "South Indian rice flavored with coconut and spices.",
        "ingredients": "Cooked Rice, Coconut, Green Chilli, Peanuts, Mustard Seeds, Curry Leaves, Salt, Oil",
        "instructions": "1. Heat oil. 2. Add mustard seeds and peanuts. 3. Add curry leaves and chilli. 4. Add coconut. 5. Mix with cooked rice.",
        "cooking_time": 20,
        "calories": 340,
        "protein": 7,
        "carbohydrates": 52,
        "fat": 11
    },

    {
        "name": "Jeera Rice",
        "description": "Simple basmati rice flavored with cumin.",
        "ingredients": "Basmati Rice, Cumin, Butter, Salt, Water",
        "instructions": "1. Wash rice. 2. Fry cumin in butter. 3. Add rice and water. 4. Add salt. 5. Cook until rice is fluffy.",
        "cooking_time": 25,
        "calories": 280,
        "protein": 5,
        "carbohydrates": 48,
        "fat": 7
    },

    {
        "name": "Gobi Manchurian",
        "description": "Crispy cauliflower tossed in Indo-Chinese sauce.",
        "ingredients": "Cauliflower, Corn Flour, Onion, Capsicum, Garlic, Soy Sauce, Pepper, Salt, Oil",
        "instructions": "1. Coat cauliflower with batter. 2. Fry until crispy. 3. Prepare sauce. 4. Add cauliflower. 5. Toss and serve.",
        "cooking_time": 40,
        "calories": 350,
        "protein": 8,
        "carbohydrates": 38,
        "fat": 17
    }

]


with app.app_context():

    added = 0

    for data in recipes:

        # Don't add duplicate recipes
        existing = Recipe.query.filter_by(
            name=data["name"]
        ).first()

        if existing:
            continue

        recipe = Recipe(**data)

        db.session.add(recipe)

        added += 1

    db.session.commit()

    print(f"Successfully added {added} new recipes.")