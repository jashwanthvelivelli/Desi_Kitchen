# database.py - SQLAlchemy database setup for Desi Kitchen.
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Connect SQLAlchemy with the Flask app and create missing tables."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
