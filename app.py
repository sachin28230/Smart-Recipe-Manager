from flask import Flask, render_template, request, redirect, url_for, session, flash, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Mail, Message
from recommendation import (
    get_recommendations,
    get_ingredient_ml_scores,
    get_personalized_recommendations
)
from smtplib import SMTPAuthenticationError
import random
import requests
import hashlib
import os

from dotenv import load_dotenv
from datetime import datetime, timedelta


def is_strong_password(password):
    """
    Validate the password rules used by the application.

    Requirements:
    - At least 8 characters
    - At least 1 uppercase letter
    - At least 1 lowercase letter
    - At least 1 number
    - At least 1 special character
    """
    return (
        len(password) >= 8
        and any(char.isupper() for char in password)
        and any(char.islower() for char in password)
        and any(char.isdigit() for char in password)
        and any(not char.isalnum() for char in password)
    )

# Load the backend settings even when Flask is started from the project root.
load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))
print("MAIL USERNAME LOADED:", os.getenv("MAIL_USERNAME"))
print("MAIL PASSWORD LENGTH:", len(os.getenv("MAIL_PASSWORD", "")))

app = Flask(__name__)

app.secret_key = "smart-recipe-making-secret-key"

# PostgreSQL database connection
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Initialize database
db = SQLAlchemy(app)

# Email configuration
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USERNAME"] = os.getenv("MAIL_USERNAME", "").strip()
app.config["MAIL_PASSWORD"] = os.getenv("MAIL_PASSWORD", "").strip().replace(" ", "")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("MAIL_USERNAME")

mail = Mail(app)

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    name = db.Column(
        db.String(100),
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )

    is_verified = db.Column(
        db.Boolean,
        default=False
    )

    is_admin = db.Column(
        db.Boolean,
        default=False
    )

    phone_number = db.Column(
        db.String(20)
    )

class OTPVerification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    otp_hash = db.Column(db.String(64), nullable=False)
    expires_at = db.Column(db.DateTime, nullable=False)
    attempts = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    instructions = db.Column(db.Text, nullable=False)
    cooking_time = db.Column(db.Integer, nullable=False)
    calories = db.Column(db.Integer)
    protein = db.Column(db.Float)
    carbohydrates = db.Column(db.Float)
    fat = db.Column(db.Float)
    nutrition_tips = db.Column(db.Text)

class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    recipe_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "recipe_id",
            name="unique_user_recipe"
        ),
    )


class RecipeReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer, nullable=False)
    recipe_id = db.Column(db.Integer, nullable=False)

    rating = db.Column(db.Integer, nullable=False)
    review = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    __table_args__ = (
        db.UniqueConstraint(
            "user_id",
            "recipe_id",
            name="unique_user_recipe_review"
        ),
    )
def search_mealdb(query):
    url = "https://www.themealdb.com/api/json/v1/1/search.php"

    try:
        response = requests.get(
            url,
            params={"s": query},
            timeout=10
        )

        if response.status_code != 200:
            return []

        data = response.json()

        return data.get("meals") or []

    except requests.RequestException:
        return []

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        # Get form data
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        phone_number = request.form.get("phone_number", "").strip()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        # Check required fields
        if not name or not email or not password or not confirm_password:
            return "Please fill in all fields."
        if not phone_number.isdigit() or len(phone_number) != 10:
            return "Please enter a valid 10-digit mobile number."

        # Check passwords
        if password != confirm_password:
            return "Passwords do not match. Please go back and try again."

        # Check password strength on the server
        if not is_strong_password(password):
            return """
            <h3>❌ Password does not meet the security requirements.</h3>
            <p>Your password must contain:</p>
            <ul>
                <li>At least 8 characters</li>
                <li>At least 1 uppercase letter</li>
                <li>At least 1 lowercase letter</li>
                <li>At least 1 number</li>
                <li>At least 1 special character</li>
            </ul>
            <a href="/register">← Go back to Registration</a>
            """

        # Check if email already exists
        existing_user = User.query.filter_by(email=email).first()

        # ------------------------------------------------
        # CASE 1: EMAIL ALREADY VERIFIED
        # ------------------------------------------------
        if existing_user and existing_user.is_verified:
         return """
    <h3>Email already registered and verified.</h3>
    <p>Please login to continue.</p>
    <a href="/login">Go to Login</a>
    """

        # Hash password
        hashed_password = generate_password_hash(password)

        # ------------------------------------------------
        # CASE 2: EMAIL EXISTS BUT IS NOT VERIFIED
        # ------------------------------------------------
        if existing_user:

            new_user = existing_user

            # Update the user's details
            new_user.name = name
            new_user.password = hashed_password
            new_user.phone_number = phone_number

        # ------------------------------------------------
        # CASE 3: NEW EMAIL
        # ------------------------------------------------
        else:

            new_user = User(
    name=name,
    email=email,
    password=hashed_password,
    phone_number=phone_number
)

            db.session.add(new_user)

        # Get user ID without creating duplicate user
        db.session.flush()

        # Generate a new 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Hash OTP
        otp_hash = hashlib.sha256(
            otp.encode()
        ).hexdigest()

        # OTP expires after 5 minutes
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        # Create OTP record
        new_otp = OTPVerification(
            user_id=new_user.id,
            otp_hash=otp_hash,
            expires_at=expires_at,
            attempts=0
        )

        db.session.add(new_otp)

        # ------------------------------------------------
        # SEND OTP EMAIL
        # ------------------------------------------------
        try:

            msg = Message(
                subject="Smart Recipe Making - Email Verification",
                sender=app.config["MAIL_USERNAME"],
                recipients=[email]
            )

            msg.body = f"""
Hello {name},

Your Smart Recipe Making verification OTP is:

{otp}

This OTP is valid for 5 minutes.

If you did not request this OTP, please ignore this email.

Regards,
Smart Recipe Making
"""

            mail.send(msg)

        except Exception as e:

            print("EMAIL ERROR:", type(e).__name__, str(e))

            db.session.rollback()

            return (
                f"Email sending failed: {type(e).__name__}: {str(e)}"
            ), 503

        # Save user and OTP
        db.session.commit()

        # Go to OTP verification page
        return redirect(
            url_for("verify_otp", email=email)
        )

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please enter your email and password.", "error")
            return redirect(url_for("login"))

        # Find user in database
        user = User.query.filter_by(email=email).first()

        if user is None:
            flash("Email not registered. Please create an account first.", "error")
            return redirect(url_for("login"))

        # Check password
        if not check_password_hash(user.password, password):
            flash("Incorrect password. Please try again.", "error")
            return redirect(url_for("login"))

        # Check email verification
        if not user.is_verified:
            return """
            <h3>Email not verified.</h3>
            <p>Please verify your email with the OTP before logging in.</p>
            <a href="/verify-otp?email={}">Verify Email</a>
            """.format(email)

        # Store login information
        session["user_id"] = user.id
        session["user_name"] = user.name
        session["user_email"] = user.email

        # Admin goes to Admin Dashboard
        if user.is_admin:
            return redirect(url_for("admin_dashboard"))

        # Normal user goes to normal Dashboard
        return redirect(url_for("dashboard"))

    return render_template("login.html")

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get_or_404(session["user_id"])

    # Admin users should stay in Admin Dashboard
    if user.is_admin:
        return redirect(url_for("admin_dashboard"))

    # Get all recipes
    all_recipes = Recipe.query.all()

    # Get this user's favorite recipes
    favorite_records = Favorite.query.filter_by(
        user_id=user.id
    ).all()

    favorite_recipe_ids = [
        favorite.recipe_id
        for favorite in favorite_records
    ]

    # Generate personalized ML recommendations
    personalized_recommendations = (
        get_personalized_recommendations(
            all_recipes,
            favorite_recipe_ids,
            number_of_recommendations=5
        )
    )

    return render_template(
        "dashboard.html",
        user_name=user.name,
        personalized_recommendations=personalized_recommendations
    )
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/verify-otp", methods=["GET", "POST"])
def verify_otp():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()
        entered_otp = request.form.get("otp", "").strip()

        # Check email
        if not email:
            return "Email is required."

        # Check OTP
        if not entered_otp:
            return "Please enter the OTP."

        # Find user
        user = User.query.filter_by(email=email).first()

        if user is None:
            return "User not found. Please register first."

        # If already verified, go directly to login
        if user.is_verified:
            return redirect(url_for("login"))

        # Get the latest OTP
        otp_record = OTPVerification.query.filter_by(
            user_id=user.id
        ).order_by(
            OTPVerification.id.desc()
        ).first()

        # No OTP found
        if otp_record is None:
            return f"""
            <h3>OTP not found.</h3>
            <p>Please request a new OTP.</p>
            <a href="/resend-otp?email={email}">Resend OTP</a>
            """

        # Check whether OTP has expired
        if datetime.utcnow() > otp_record.expires_at:
            return f"""
            <h3>OTP has expired.</h3>
            <p>Please request a new OTP.</p>
            <a href="/resend-otp?email={email}">Resend OTP</a>
            """

        # Check whether this OTP has already reached 5 attempts
        if otp_record.attempts >= 5:
            return f"""
            <h3>Too many incorrect attempts.</h3>
            <p>This OTP has been blocked.</p>
            <p>Please request a new OTP.</p>
            <a href="/resend-otp?email={email}">Resend OTP</a>
            """

        # Check OTP format
        if len(entered_otp) != 6 or not entered_otp.isdigit():
            return """
            <h3>Invalid OTP format.</h3>
            <p>Please enter the 6-digit OTP.</p>
            <a href="javascript:history.back()">Try Again</a>
            """

        # Hash entered OTP
        entered_otp_hash = hashlib.sha256(
            entered_otp.encode()
        ).hexdigest()

        # Check whether OTP is correct
        if entered_otp_hash != otp_record.otp_hash:

            otp_record.attempts += 1
            db.session.commit()

            if otp_record.attempts >= 5:
                return f"""
                <h3>Too many incorrect attempts.</h3>
                <p>This OTP has been blocked.</p>
                <p>Please request a new OTP.</p>
                <a href="/resend-otp?email={email}">Resend OTP</a>
                """

            remaining_attempts = 5 - otp_record.attempts

            return f"""
            <h3>Invalid OTP.</h3>
            <p>Please check your OTP and try again.</p>
            <p>Attempts remaining: {remaining_attempts}</p>
            <a href="/verify-otp?email={email}">Try Again</a>
            """

        # OTP is correct
        user.is_verified = True

        db.session.delete(otp_record)

        db.session.commit()

        # Email verification completed.
        # Continue to the normal login page.
        return redirect(
            url_for("login")
        )

    # GET request
    email = request.args.get("email", "").strip().lower()

    if not email:
        return redirect(url_for("register"))

    return render_template(
        "verify_otp.html",
        email=email
    )


@app.route("/resend-otp")
def resend_otp():

    email = request.args.get("email", "").strip().lower()

    if not email:
        return "Email is required."

    # Find the user
    user = User.query.filter_by(email=email).first()

    if user is None:
        return "User not found. Please register first."

    # Don't resend OTP to an already verified account
    if user.is_verified:
        return """
        <h3>Email is already verified.</h3>
        <p>Please login to continue.</p>
        <a href="/login">Go to Login</a>
        """

    # Generate a new 6-digit OTP
    otp = str(random.randint(100000, 999999))

    # Hash the OTP
    otp_hash = hashlib.sha256(
        otp.encode()
    ).hexdigest()

    # New OTP expires after 5 minutes
    expires_at = datetime.utcnow() + timedelta(minutes=5)

    # Save new OTP
    new_otp = OTPVerification(
        user_id=user.id,
        otp_hash=otp_hash,
        expires_at=expires_at,
        attempts=0
    )

    db.session.add(new_otp)

    # Send the new OTP
    try:

        msg = Message(
            subject="Smart Recipe Making - New Verification OTP",
            sender=app.config["MAIL_USERNAME"],
            recipients=[email]
        )

        msg.body = f"""
Hello {user.name},

Your new Smart Recipe Making verification OTP is:

{otp}

This OTP is valid for 5 minutes.

Your previous OTP is no longer valid.

Regards,
Smart Recipe Making
"""

        mail.send(msg)

    except Exception as e:

        print("RESEND OTP EMAIL ERROR:", type(e).__name__, str(e))

        db.session.rollback()

        return (
            f"Email sending failed: {type(e).__name__}: {str(e)}"
        ), 503

    db.session.commit()

    return redirect(
        url_for("verify_otp", email=email)
    )
@app.route("/add-recipes")
def add_recipes():

    recipes = [
        Recipe(
            name="Chicken Biryani",
            description="A flavorful rice dish prepared with chicken, spices and aromatic basmati rice.",
            ingredients="Chicken, Basmati Rice, Onion, Tomato, Ginger, Garlic, Yogurt, Biryani Masala, Salt, Oil",
            instructions="1. Marinate the chicken with yogurt and spices. 2. Cook the chicken. 3. Prepare the basmati rice. 4. Layer rice and chicken. 5. Cook on low heat until done.",
            cooking_time=60,
            calories=650,
            protein=35,
            carbohydrates=75,
            fat=22
        ),

        Recipe(
            name="Masala Dosa",
            description="A crispy South Indian dosa filled with spiced potato masala.",
            ingredients="Rice, Urad Dal, Potato, Onion, Green Chilli, Mustard Seeds, Turmeric, Salt, Oil",
            instructions="1. Prepare dosa batter. 2. Ferment the batter. 3. Prepare potato masala. 4. Spread batter on a hot pan. 5. Add potato masala and serve.",
            cooking_time=40,
            calories=350,
            protein=8,
            carbohydrates=55,
            fat=10
        ),

        Recipe(
            name="Vegetable Fried Rice",
            description="Quick and delicious fried rice prepared with mixed vegetables and rice.",
            ingredients="Cooked Rice, Carrot, Beans, Capsicum, Spring Onion, Soy Sauce, Pepper, Salt, Oil",
            instructions="1. Heat oil in a pan. 2. Add vegetables. 3. Stir-fry the vegetables. 4. Add cooked rice. 5. Add soy sauce and seasoning. 6. Mix well and serve.",
            cooking_time=25,
            calories=420,
            protein=9,
            carbohydrates=68,
            fat=12
        ),

        Recipe(
            name="Paneer Butter Masala",
            description="Creamy Indian curry made with paneer, tomato and butter.",
            ingredients="Paneer, Tomato, Onion, Butter, Cream, Ginger, Garlic, Garam Masala, Salt",
            instructions="1. Prepare tomato gravy. 2. Add spices. 3. Add butter and cream. 4. Add paneer cubes. 5. Cook for a few minutes and serve.",
            cooking_time=35,
            calories=480,
            protein=18,
            carbohydrates=20,
            fat=32
        )
    ]

    for recipe in recipes:
        existing_recipe = Recipe.query.filter_by(name=recipe.name).first()

        if not existing_recipe:
            db.session.add(recipe)

    db.session.commit()

    return "Sample recipes added successfully!"
@app.route("/recipe-image/<int:recipe_id>")
def recipe_image(recipe_id):

    recipe = Recipe.query.get_or_404(recipe_id)

    recipe_name = recipe.name.strip().lower()

    # =====================================================
    # LOCAL RECIPE IMAGE MAPPING
    # =====================================================

    local_images = {

        "chicken biryani": "hero-food.jpg",

        # Add your other exact recipe-to-image mappings here
        # after we identify the corresponding uploaded photos.

    }

    # Check whether this recipe has one of your uploaded images
    if recipe_name in local_images:

        image_name = local_images[recipe_name]

        image_path = os.path.join(
            app.static_folder,
            "images",
            image_name
        )

        if os.path.exists(image_path):

            return send_from_directory(
                os.path.join(
                    app.static_folder,
                    "images"
                ),
                image_name
            )


    # =====================================================
    # THEMEALDB FALLBACK
    # =====================================================

    url = "https://www.themealdb.com/api/json/v1/1/search.php"

    try:

        response = requests.get(
            url,
            params={"s": recipe.name},
            timeout=10
        )

        if response.status_code == 200:

            data = response.json()

            meals = data.get("meals") or []

            requested_name = recipe_name

            # Exact match first
            for meal in meals:

                meal_name = (
                    meal.get("strMeal") or ""
                ).strip().lower()

                if meal_name == requested_name:

                    image_url = meal.get(
                        "strMealThumb"
                    )

                    if image_url:

                        return redirect(
                            image_url
                        )

    except requests.RequestException:
        pass


    # No matching image found
    return "", 404
@app.route("/recipe/<int:recipe_id>")
def recipe(recipe_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    recipe = Recipe.query.get_or_404(recipe_id)

    # Get all recipes from database
    all_recipes = Recipe.query.all()

    # Generate ML recommendations
    recommendations = get_recommendations(
        all_recipes,
        recipe.id,
        number_of_recommendations=5
    )

    # Get reviews for this recipe
    reviews = RecipeReview.query.filter_by(
        recipe_id=recipe.id
    ).order_by(
        RecipeReview.created_at.desc()
    ).all()

    # Calculate average rating
    average_rating = None

    if reviews:
        average_rating = round(
            sum(review.rating for review in reviews) / len(reviews),
            1
        )

    # Check whether the logged-in user has already reviewed this recipe
    user_review = RecipeReview.query.filter_by(
        user_id=session["user_id"],
        recipe_id=recipe.id
    ).first()

    return render_template(
        "recipe.html",
        recipe=recipe,
        recommendations=recommendations,
        reviews=reviews,
        average_rating=average_rating,
        review_count=len(reviews),
        user_review=user_review
    )

@app.route("/review/<int:recipe_id>", methods=["POST"])
def add_review(recipe_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    recipe = Recipe.query.get_or_404(recipe_id)

    rating = request.form.get("rating", "").strip()
    review_text = request.form.get("review", "").strip()

    # Validate rating
    if not rating.isdigit():
        return "Please select a rating between 1 and 5."

    rating = int(rating)

    if rating < 1 or rating > 5:
        return "Rating must be between 1 and 5."

    # Prevent duplicate review by the same user
    existing_review = RecipeReview.query.filter_by(
        user_id=session["user_id"],
        recipe_id=recipe.id
    ).first()

    if existing_review:
        return """
        <h3>You have already reviewed this recipe.</h3>
        <a href="/recipe/{}">← Back to Recipe</a>
        """.format(recipe.id)

    new_review = RecipeReview(
        user_id=session["user_id"],
        recipe_id=recipe.id,
        rating=rating,
        review=review_text
    )

    db.session.add(new_review)
    db.session.commit()

    return redirect(url_for("recipe", recipe_id=recipe.id))


@app.route("/favorite/<int:recipe_id>", methods=["POST"])
def favorite(recipe_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    recipe = Recipe.query.get_or_404(recipe_id)

    existing_favorite = Favorite.query.filter_by(
        user_id=user_id,
        recipe_id=recipe.id
    ).first()

    if existing_favorite:
        db.session.delete(existing_favorite)
    else:
        new_favorite = Favorite(
            user_id=user_id,
            recipe_id=recipe.id
        )
        db.session.add(new_favorite)

    db.session.commit()

    return redirect(url_for("recipe", recipe_id=recipe.id))
@app.route("/favorites")
def favorites():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]

    favorite_records = Favorite.query.filter_by(
        user_id=user_id
    ).order_by(
        Favorite.created_at.desc()
    ).all()

    favorite_recipes = []

    for favorite in favorite_records:
        recipe = Recipe.query.get(favorite.recipe_id)

        if recipe:
            favorite_recipes.append(recipe)

    return render_template(
        "favorites.html",
        favorite_recipes=favorite_recipes
    )
@app.route("/profile")
def profile():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get_or_404(session["user_id"])

    return render_template(
        "profile.html",
        user=user
    )
@app.route("/update-profile", methods=["POST"])
def update_profile():

    # Check if user is logged in
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Get logged-in user
    user = User.query.get_or_404(session["user_id"])

    # Get form data
    name = request.form.get("name", "").strip()
    email = request.form.get("email", "").strip().lower()
    phone_number = request.form.get("phone_number", "").strip()

    # Validate fields
    if not name or not email or not phone_number:
        return "Name, email and mobile number are required."

    if not phone_number.isdigit() or len(phone_number) != 10:
        return "Please enter a valid 10-digit mobile number."

    # Check whether email is already used by another account
    existing_user = User.query.filter(
        User.email == email,
        User.id != user.id
    ).first()

    if existing_user:
        return """
        <h3>Email already exists.</h3>
        <p>Please use a different email address.</p>
        <a href="/profile">← Back to Profile</a>
        """

    # Update user information
    user.name = name
    user.email = email
    user.phone_number = phone_number

    # Save changes
    db.session.commit()

    # Update session information
    session["user_name"] = user.name
    session["user_email"] = user.email

    # Redirect back to profile
    return redirect(url_for("profile"))
@app.route("/change-password", methods=["POST"])
def change_password():

    # Check if user is logged in
    if "user_id" not in session:
        return redirect(url_for("login"))

    # Get logged-in user
    user = User.query.get_or_404(session["user_id"])

    # Get form data
    current_password = request.form.get("current_password", "")
    new_password = request.form.get("new_password", "")
    confirm_password = request.form.get("confirm_password", "")

    # Check all fields
    if not current_password or not new_password or not confirm_password:
        return """
        <h3>Please fill in all password fields.</h3>
        <a href="/profile">← Back to Profile</a>
        """

    # Check current password
    if not check_password_hash(user.password, current_password):
        return """
        <h3>❌ Current password is incorrect.</h3>
        <a href="/profile">← Back to Profile</a>
        """

    # Check new password confirmation
    if new_password != confirm_password:
        return """
        <h3>❌ New passwords do not match.</h3>
        <a href="/profile">← Back to Profile</a>
        """

    # Check password strength
    if not is_strong_password(new_password):
        return """
        <h3>❌ New password does not meet the security requirements.</h3>
        <p>Your password must contain:</p>
        <ul>
            <li>At least 8 characters</li>
            <li>At least 1 uppercase letter</li>
            <li>At least 1 lowercase letter</li>
            <li>At least 1 number</li>
            <li>At least 1 special character</li>
        </ul>
        <a href="/profile">← Back to Profile</a>
        """

    # Prevent using the same password
    if check_password_hash(user.password, new_password):
        return """
        <h3>❌ New password must be different from your current password.</h3>
        <a href="/profile">← Back to Profile</a>
        """

    # Hash the new password
    user.password = generate_password_hash(new_password)

    # Save to database
    db.session.commit()

    return redirect(url_for("profile"))
@app.route("/admin")
def admin_dashboard():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get_or_404(session["user_id"])

    if not user.is_admin:
        return "Access denied. Admins only.", 403

    recipes = Recipe.query.order_by(Recipe.id.desc()).all()

    user_query = request.args.get("user_query", "").strip()

    if user_query:
        search_text = f"%{user_query}%"
        users = User.query.filter(
            db.or_(
                User.name.ilike(search_text),
                User.email.ilike(search_text),
                User.phone_number.ilike(search_text)
            )
        ).order_by(User.id.desc()).all()
    else:
        users = User.query.order_by(User.id.desc()).all()

    return render_template(
        "admin.html",
        user=user,
        recipes=recipes,
        users=users,
        user_query=user_query
    )
@app.route("/admin/add-recipe", methods=["GET", "POST"])
def admin_add_recipe():

    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get_or_404(session["user_id"])

    if not user.is_admin:
        return "Access denied. Admins only.", 403

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        ingredients = request.form.get("ingredients", "").strip()
        instructions = request.form.get("instructions", "").strip()

        cooking_time = request.form.get("cooking_time", "").strip()
        calories = request.form.get("calories", "").strip()
        protein = request.form.get("protein", "").strip()
        carbohydrates = request.form.get("carbohydrates", "").strip()
        fat = request.form.get("fat", "").strip()
        nutrition_tips = request.form.get("nutrition_tips", "").strip()

        if not name or not description or not ingredients or not instructions:
            return "Please fill in all required fields."

        new_recipe = Recipe(
            name=name,
            description=description,
            ingredients=ingredients,
            instructions=instructions,
            cooking_time=int(cooking_time or 0),
            calories=int(calories or 0),
            protein=float(protein or 0),
            carbohydrates=float(carbohydrates or 0),
            fat=float(fat or 0),
            nutrition_tips=nutrition_tips
        )

        db.session.add(new_recipe)
        db.session.commit()

        return redirect(url_for("admin_dashboard"))

    return render_template("admin_add_recipe.html")
@app.route("/admin/edit-recipe/<int:recipe_id>", methods=["GET", "POST"])
def admin_edit_recipe(recipe_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get_or_404(session["user_id"])

    if not user.is_admin:
        return "Access denied. Admins only.", 403

    recipe = Recipe.query.get_or_404(recipe_id)

    if request.method == "POST":
        recipe.name = request.form.get("name", "").strip()
        recipe.description = request.form.get("description", "").strip()
        recipe.ingredients = request.form.get("ingredients", "").strip()
        recipe.instructions = request.form.get("instructions", "").strip()
        recipe.cooking_time = int(request.form.get("cooking_time", 0) or 0)
        recipe.calories = int(request.form.get("calories", 0) or 0)
        recipe.protein = float(request.form.get("protein", 0) or 0)
        recipe.carbohydrates = float(request.form.get("carbohydrates", 0) or 0)
        recipe.fat = float(request.form.get("fat", 0) or 0)
        recipe.nutrition_tips = request.form.get("nutrition_tips", "").strip()

        db.session.commit()

        return redirect(url_for("admin_dashboard"))

    return render_template(
        "admin_edit_recipe.html",
        recipe=recipe
    )
@app.route("/admin/delete-recipe/<int:recipe_id>", methods=["POST"])
def admin_delete_recipe(recipe_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get_or_404(session["user_id"])

    if not user.is_admin:
        return "Access denied. Admins only.", 403

    recipe = Recipe.query.get_or_404(recipe_id)

    # Delete related favorites first
    Favorite.query.filter_by(recipe_id=recipe.id).delete()

    # Delete related reviews
    RecipeReview.query.filter_by(recipe_id=recipe.id).delete()

    # Delete the recipe
    db.session.delete(recipe)
    db.session.commit()

    return redirect(url_for("admin_dashboard"))

@app.route("/admin/delete-user/<int:user_id>", methods=["POST"])
def admin_delete_user(user_id):

    if "user_id" not in session:
        return redirect(url_for("login"))

    admin_user = User.query.get_or_404(session["user_id"])

    if not admin_user.is_admin:
        return "Access denied. Admins only.", 403

    account = User.query.get_or_404(user_id)

    # Never allow an admin to delete their own account.
    if account.id == admin_user.id:
        return """
        <h3>❌ You cannot delete your own admin account.</h3>
        <a href="/admin">← Back to Admin Dashboard</a>
        """

    # Keep admin accounts protected from this normal-user delete action.
    if account.is_admin:
        return """
        <h3>❌ Admin accounts cannot be deleted from this page.</h3>
        <a href="/admin">← Back to Admin Dashboard</a>
        """

    # Remove data belonging to the user before deleting the account.
    Favorite.query.filter_by(user_id=account.id).delete()
    RecipeReview.query.filter_by(user_id=account.id).delete()
    OTPVerification.query.filter_by(user_id=account.id).delete()

    db.session.delete(account)
    db.session.commit()

    return redirect(url_for("admin_dashboard"))

@app.route("/test-mealdb")
def test_mealdb():
    url = "https://www.themealdb.com/api/json/v1/1/search.php?s=chicken"

    response = requests.get(url, timeout=10)

    if response.status_code != 200:
        return "TheMealDB API connection failed."

    data = response.json()

    return data


@app.route("/search")
def search():
    query = request.args.get("query", "").strip()

    if not query:
        return redirect(url_for("dashboard"))

    # Search local PostgreSQL recipes
    search_text = f"%{query}%"

    recipes = Recipe.query.filter(
        db.or_(
            Recipe.name.ilike(search_text),
            Recipe.ingredients.ilike(search_text),
            Recipe.description.ilike(search_text)
        )
    ).all()

    # Search global recipes from TheMealDB
    external_recipes = search_mealdb(query)

    return render_template(
        "search_results.html",
        recipes=recipes,
        external_recipes=external_recipes,
        query=query
    )
@app.route("/global-recipe/<int:meal_id>")
def global_recipe(meal_id):

    url = "https://www.themealdb.com/api/json/v1/1/lookup.php"

    try:
        response = requests.get(
            url,
            params={"i": meal_id},
            timeout=10
        )

        if response.status_code != 200:
            return "Unable to connect to recipe service."

        data = response.json()
        meals = data.get("meals") or []

        if not meals:
            return "Recipe not found."

        meal = meals[0]

        return render_template(
            "global_recipe.html",
            meal=meal
        )

    except requests.RequestException:
        return "Unable to connect to recipe service."


@app.route("/smart-search")
def smart_search():
    ingredients_input = request.args.get("ingredients", "").strip()

    if not ingredients_input:
        return redirect(url_for("dashboard"))

    user_ingredients = list(dict.fromkeys(
        item.strip().lower()
        for item in ingredients_input.split(",")
        if item.strip()
    ))

    if not user_ingredients:
        return redirect(url_for("dashboard"))

    # Search recipes stored in PostgreSQL
    recipes = Recipe.query.all()

    ml_scores = get_ingredient_ml_scores(
        recipes,
        ingredients_input
    )

    matching_recipes = []

    for recipe in recipes:
        recipe_ingredients = [
            item.strip().lower()
            for item in (recipe.ingredients or "").split(",")
            if item.strip()
        ]

        matched_ingredients = []

        for user_ingredient in user_ingredients:
            if any(
                user_ingredient == recipe_ingredient
                or user_ingredient in recipe_ingredient
                or recipe_ingredient in user_ingredient
                for recipe_ingredient in recipe_ingredients
            ):
                matched_ingredients.append(user_ingredient)

        matched_ingredients = list(set(matched_ingredients))

        if matched_ingredients:
            match_percentage = round(
                len(matched_ingredients)
                / len(user_ingredients) * 100
            )

            ml_similarity = round(
                ml_scores.get(recipe.id, 0) * 100
            )

            combined_score = round(
                match_percentage * 0.7 + ml_similarity * 0.3
            )

            matching_recipes.append({
                "recipe": recipe,
                "matched_ingredients": matched_ingredients,
                "match_percentage": match_percentage,
                "ml_similarity": ml_similarity,
                "combined_score": combined_score,
                "matched_count": len(matched_ingredients)
            })

    matching_recipes.sort(
        key=lambda item: item["combined_score"],
        reverse=True
    )

    # Search TheMealDB with a small request limit
    external_recipes = []
    seen_meal_ids = set()
    max_detail_requests = 2
    detail_requests = 0

    for ingredient in user_ingredients[:2]:
        try:
            response = requests.get(
                "https://www.themealdb.com/api/json/v1/1/filter.php",
                params={"i": ingredient},
                timeout=3
            )

            if response.status_code != 200:
                continue

            meals = response.json().get("meals") or []

        except (requests.RequestException, ValueError):
            continue

        for meal in meals:
            meal_id = meal.get("idMeal")

            if not meal_id or meal_id in seen_meal_ids:
                continue

            seen_meal_ids.add(meal_id)

            if detail_requests >= max_detail_requests:
                break

            detail_requests += 1

            try:
                detail_response = requests.get(
                    "https://www.themealdb.com/api/json/v1/1/lookup.php",
                    params={"i": meal_id},
                    timeout=3
                )

                if detail_response.status_code != 200:
                    continue

                detail_meals = (
                    detail_response.json().get("meals") or []
                )

                if not detail_meals:
                    continue

                complete_meal = detail_meals[0]

            except (requests.RequestException, ValueError):
                continue

            recipe_ingredients = []

            for i in range(1, 21):
                value = complete_meal.get(f"strIngredient{i}")

                if value and value.strip():
                    recipe_ingredients.append(value.strip().lower())

            matched_global_ingredients = []

            for user_ingredient in user_ingredients:
                if any(
                    user_ingredient == recipe_ingredient
                    or user_ingredient in recipe_ingredient
                    or recipe_ingredient in user_ingredient
                    for recipe_ingredient in recipe_ingredients
                ):
                    matched_global_ingredients.append(user_ingredient)

            matched_global_ingredients = list(
                set(matched_global_ingredients)
            )

            complete_meal["matched_ingredients"] = (
                matched_global_ingredients
            )

            complete_meal["match_percentage"] = round(
                len(matched_global_ingredients)
                / len(user_ingredients) * 100
            )

            complete_meal["matched_count"] = len(
                matched_global_ingredients
            )

            external_recipes.append(complete_meal)

        if detail_requests >= max_detail_requests:
            break

    external_recipes.sort(
        key=lambda meal: (
            meal.get("match_percentage", 0),
            meal.get("matched_count", 0)
        ),
        reverse=True
    )

    return render_template(
        "smart_results.html",
        matching_recipes=matching_recipes,
        external_recipes=external_recipes[:10],
        ingredients_input=ingredients_input
    )



@app.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():

    if request.method == "POST":

        email = request.form.get("email", "").strip().lower()

        if not email:
            return "Please enter your email address."

        user = User.query.filter_by(email=email).first()

        if user is None:
            return """
            <h3>Email not registered.</h3>
            <p>Please check your email address.</p>
            <a href="/forgot-password">← Try Again</a>
            """

        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # Hash OTP before storing it
        otp_hash = hashlib.sha256(
            otp.encode()
        ).hexdigest()

        # OTP expires after 5 minutes
        expires_at = datetime.utcnow() + timedelta(minutes=5)

        # Remove previous password-reset OTPs
        OTPVerification.query.filter_by(
            user_id=user.id
        ).delete()

        # Create new OTP record
        reset_otp = OTPVerification(
            user_id=user.id,
            otp_hash=otp_hash,
            expires_at=expires_at,
            attempts=0
        )

        db.session.add(reset_otp)
        db.session.commit()

        # Send OTP through Gmail
        message = Message(
            subject="Smart Recipe Making - Password Reset OTP",
            recipients=[user.email]
        )

        message.body = f"""
Hello {user.name},

We received a request to reset your Smart Recipe Making password.

Your password reset OTP is:

{otp}

This OTP is valid for 5 minutes.

If you did not request a password reset, please ignore this email.

Regards,
Smart Recipe Making
"""

        mail.send(message)

        # Store reset email in session
        session["reset_email"] = user.email

        return redirect(
            url_for(
                "reset_password",
                email=user.email
            )
        )

    return render_template("forgot_password.html")
@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():

    email = request.args.get("email") or session.get("reset_email")

    if not email:
        return redirect(url_for("forgot_password"))

    user = User.query.filter_by(
        email=email.lower()
    ).first()

    if user is None:
        return redirect(url_for("forgot_password"))

    if request.method == "POST":

        otp = request.form.get("otp", "").strip()

        if not otp:
            return "Please enter the OTP."

        otp_record = OTPVerification.query.filter_by(
            user_id=user.id
        ).order_by(
            OTPVerification.id.desc()
        ).first()

        if otp_record is None:
            return """
            <h3>❌ No OTP found.</h3>
            <a href="/forgot-password">Request a new OTP</a>
            """

        # Check OTP expiry
        if datetime.utcnow() > otp_record.expires_at:
            return """
            <h3>❌ OTP has expired.</h3>
            <a href="/forgot-password">Request a new OTP</a>
            """

        # Check maximum attempts
        if otp_record.attempts >= 5:
            return """
            <h3>❌ Too many incorrect attempts.</h3>
            <a href="/forgot-password">Request a new OTP</a>
            """

        # Hash entered OTP
        entered_hash = hashlib.sha256(
            otp.encode()
        ).hexdigest()

        # Verify OTP
        if entered_hash != otp_record.otp_hash:

            otp_record.attempts += 1

            db.session.commit()

            remaining = 5 - otp_record.attempts

            return f"""
            <h3>❌ Incorrect OTP.</h3>
            <p>Attempts remaining: {remaining}</p>
            <a href="/reset-password?email={user.email}">
                Try Again
            </a>
            """

        # OTP is correct
        session["reset_user_id"] = user.id

        return redirect(
            url_for(
                "set_new_password"
            )
        )

    return render_template(
        "reset_password.html",
        email=user.email
    )
@app.route("/set-new-password", methods=["GET", "POST"])
def set_new_password():

    # Check whether OTP verification was completed
    if "reset_user_id" not in session:
        return redirect(url_for("forgot_password"))

    user = User.query.get_or_404(
        session["reset_user_id"]
    )

    if request.method == "POST":

        new_password = request.form.get(
            "new_password",
            ""
        )

        confirm_password = request.form.get(
            "confirm_password",
            ""
        )

        # Check fields
        if not new_password or not confirm_password:
            return """
            <h3>Please fill in both password fields.</h3>
            <a href="/set-new-password">
                ← Try Again
            </a>
            """

        # Check password match
        if new_password != confirm_password:
            return """
            <h3>❌ Passwords do not match.</h3>
            <a href="/set-new-password">
                ← Try Again
            </a>
            """

        # Check password strength
        if not is_strong_password(new_password):
            return """
            <h3>❌ Password does not meet the security requirements.</h3>
            <p>Your password must contain:</p>
            <ul>
                <li>At least 8 characters</li>
                <li>At least 1 uppercase letter</li>
                <li>At least 1 lowercase letter</li>
                <li>At least 1 number</li>
                <li>At least 1 special character</li>
            </ul>
            <a href="/set-new-password">
                ← Try Again
            </a>
            """

        # Hash new password
        user.password = generate_password_hash(
            new_password
        )

        # Save password
        db.session.commit()

        # Clear password-reset session data
        session.pop("reset_user_id", None)
        session.pop("reset_email", None)

        return redirect(url_for("login"))

    return render_template(
        "set_new_password.html",
        email=user.email
    )

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)