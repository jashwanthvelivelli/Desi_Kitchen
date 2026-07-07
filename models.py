# models.py - Simple database models used by Desi Kitchen.
from werkzeug.security import generate_password_hash, check_password_hash
from database import db


class User(db.Model):
    """Registered application user."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    inventory_items = db.relationship("Inventory", backref="user", cascade="all, delete")
    shopping_items = db.relationship("ShoppingItem", backref="user", cascade="all, delete")
    recipes = db.relationship("Recipe", backref="user", cascade="all, delete")

    def set_password(self, password):
        """Store a protected password hash."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """Return True when the password is correct."""
        return check_password_hash(self.password_hash, password)


class Inventory(db.Model):
    """Kitchen inventory item."""
    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(80), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=0)
    unit = db.Column(db.String(30), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


class ShoppingItem(db.Model):
    """Shopping list item."""
    __tablename__ = "shopping_list"

    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    purchased = db.Column(db.Boolean, default=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)


class Recipe(db.Model):
    """Recipe saved by the user."""
    __tablename__ = "recipes"

    id = db.Column(db.Integer, primary_key=True)
    recipe_name = db.Column(db.String(120), nullable=False)
    ingredients = db.Column(db.Text, nullable=False)
    steps = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
