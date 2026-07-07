# app.py - Main Flask routes for the Desi Kitchen web application.
import os
from functools import wraps

from flask import Flask, flash, redirect, render_template, request, session, url_for
from sqlalchemy import func, text

from database import db, init_db
from models import Inventory, Recipe, ShoppingItem, User

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(BASE_DIR, "database", "desikitchen.db")

app = Flask(__name__)
app.config["SECRET_KEY"] = "desi-kitchen-major-project-secret"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + DB_PATH
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
init_db(app)

def login_required(route):
    """Protect pages that need a logged-in user."""
    @wraps(route)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            flash("Please login first.", "error")
            return redirect(url_for("login"))
        return route(*args, **kwargs)

    return wrapper

def current_user():
    """Return the logged-in user object."""
    return User.query.get(session.get("user_id"))

def clean_words(text_value):
    """Split comma or line separated ingredients into lowercase words."""
    words = []
    for chunk in text_value.replace("\n", ",").split(","):
        word = chunk.strip().lower()
        if word:
            words.append(word)
    return words

@app.route("/")
def home():
    """Open dashboard for users and login for guests."""
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/register", methods=["GET", "POST"])
def register():
    """Create a new account."""
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        if User.query.filter_by(email=email).first():
            flash("Email already registered.", "error")
        else:
            user = User(name=name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            flash("Registration successful. Please login.", "success")
            return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Login using email and password."""
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        user = User.query.filter_by(email=email).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["user_name"] = user.name
            flash("Welcome to Desi Kitchen.", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "error")
    return render_template("login.html")

@app.route("/logout")
def logout():
    """End the active session."""
    session.clear()
    flash("Logged out successfully.", "success")
    return redirect(url_for("login"))

@app.route("/reset-password", methods=["GET", "POST"])
def reset_password():
    """Reset password directly when the email exists."""
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        user = User.query.filter_by(email=email).first()
        if user:
            user.set_password(request.form["password"])
            db.session.commit()
            flash("Password updated. Please login.", "success")
            return redirect(url_for("login"))
        flash("Email not found.", "error")
    return render_template("reset_password.html")

@app.route("/dashboard")
@login_required
def dashboard():
    """Show counts, low stock notifications, and recipe recommendations."""
    user_id = session["user_id"]
    total_items = Inventory.query.filter_by(user_id=user_id).count()
    low_stock = Inventory.query.filter(
        Inventory.user_id == user_id, Inventory.quantity <= 2
    ).all()
    shopping_count = ShoppingItem.query.filter_by(user_id=user_id, purchased=False).count()
    recipes = recommended_recipes(user_id)
    return render_template(
        "dashboard.html",
        total_items=total_items,
        low_stock=low_stock,
        shopping_count=shopping_count,
        recipes=recipes,
    )

def recommended_recipes(user_id):
    """Find recipes whose ingredient words exist in inventory using SQL rows."""
    recipes = db.session.execute(
        text(
            "SELECT id, recipe_name, ingredients, steps "
            "FROM recipes WHERE user_id = :uid ORDER BY lower(recipe_name)"
        ),
        {"uid": user_id},
    ).fetchall()
    rows = db.session.execute(
        text("SELECT lower(item_name) AS name FROM inventory WHERE user_id = :uid"),
        {"uid": user_id},
    ).fetchall()
    available = {row.name for row in rows}
    matched = []
    for recipe in recipes:
        ingredients = clean_words(recipe.ingredients)
        if ingredients and all(item in available for item in ingredients):
            matched.append(recipe)
    return matched

@app.route("/inventory", methods=["GET", "POST"])
@login_required
def inventory():
    """Add, search, and view inventory items."""
    user_id = session["user_id"]
    if request.method == "POST":
        item = Inventory(
            item_name=request.form["item_name"].strip(),
            category=request.form["category"].strip(),
            quantity=int(request.form["quantity"]),
            unit=request.form["unit"].strip(),
            user_id=user_id,
        )
        db.session.add(item)
        db.session.commit()
        flash("Inventory item added.", "success")
        return redirect(url_for("inventory"))
    search = request.args.get("search", "").strip()
    query = Inventory.query.filter_by(user_id=user_id)
    if search:
        query = query.filter(Inventory.item_name.ilike(f"%{search}%"))
    items = query.order_by(func.lower(Inventory.item_name)).all()
    return render_template("inventory.html", items=items, search=search, edit_item=None)

@app.route("/inventory/edit/<int:item_id>", methods=["GET", "POST"])
@login_required
def edit_inventory(item_id):
    """Edit one inventory item."""
    item = Inventory.query.filter_by(id=item_id, user_id=session["user_id"]).first_or_404()
    if request.method == "POST":
        item.item_name = request.form["item_name"].strip()
        item.category = request.form["category"].strip()
        item.quantity = int(request.form["quantity"])
        item.unit = request.form["unit"].strip()
        db.session.commit()
        flash("Inventory item updated.", "success")
        return redirect(url_for("inventory"))
    items = Inventory.query.filter_by(user_id=session["user_id"]).all()
    return render_template("inventory.html", items=items, search="", edit_item=item)

@app.route("/inventory/delete/<int:item_id>")
@login_required
def delete_inventory(item_id):
    """Delete one inventory item."""
    item = Inventory.query.filter_by(id=item_id, user_id=session["user_id"]).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash("Inventory item deleted.", "success")
    return redirect(url_for("inventory"))

@app.route("/shopping", methods=["GET", "POST"])
@login_required
def shopping():
    """Add and view shopping list items."""
    if request.method == "POST":
        item = ShoppingItem(item_name=request.form["item_name"].strip(), user_id=session["user_id"])
        db.session.add(item)
        db.session.commit()
        flash("Shopping item added.", "success")
        return redirect(url_for("shopping"))
    items = ShoppingItem.query.filter_by(user_id=session["user_id"]).order_by(ShoppingItem.purchased).all()
    return render_template("shopping.html", items=items)

@app.route("/shopping/toggle/<int:item_id>")
@login_required
def toggle_shopping(item_id):
    """Mark a shopping item as purchased or pending."""
    item = ShoppingItem.query.filter_by(id=item_id, user_id=session["user_id"]).first_or_404()
    item.purchased = not item.purchased
    db.session.commit()
    return redirect(url_for("shopping"))

@app.route("/shopping/delete/<int:item_id>")
@login_required
def delete_shopping(item_id):
    """Delete a shopping item."""
    item = ShoppingItem.query.filter_by(id=item_id, user_id=session["user_id"]).first_or_404()
    db.session.delete(item)
    db.session.commit()
    flash("Shopping item deleted.", "success")
    return redirect(url_for("shopping"))

@app.route("/recipes", methods=["GET", "POST"])
@login_required
def recipes():
    """Add, search, and view recipes."""
    user_id = session["user_id"]
    if request.method == "POST":
        recipe = Recipe(
            recipe_name=request.form["recipe_name"].strip(),
            ingredients=request.form["ingredients"].strip(),
            steps=request.form["steps"].strip(),
            user_id=user_id,
        )
        db.session.add(recipe)
        db.session.commit()
        flash("Recipe added.", "success")
        return redirect(url_for("recipes"))
    search = request.args.get("search", "").strip()
    query = Recipe.query.filter_by(user_id=user_id)
    if search:
        query = query.filter(Recipe.recipe_name.ilike(f"%{search}%"))
    recipes_list = query.order_by(func.lower(Recipe.recipe_name)).all()
    return render_template("recipes.html", recipes=recipes_list, search=search)

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """Update user name and optional password."""
    user = current_user()
    if request.method == "POST":
        user.name = request.form["name"].strip()
        password = request.form.get("password", "")
        if password:
            user.set_password(password)
        db.session.commit()
        session["user_name"] = user.name
        flash("Profile updated.", "success")
        return redirect(url_for("profile"))
    return render_template("profile.html", user=user)

if __name__ == "__main__":
    app.run(debug=True)