# DESI KITCHEN

Smart Kitchen Management System is a compact Python Flask web application for a B.Tech final year major project. It includes authentication, dashboard notifications, inventory management, shopping list, recipes, recipe recommendations, password reset, and profile update.

## Technologies

- Python 3
- Flask
- SQLite
- SQLAlchemy
- HTML, CSS, and basic JavaScript

## Run Project

```bash
pip install -r requirements.txt
python app.py
```

Open the browser at:

```text
http://127.0.0.1:5000
```

## Project Structure

```text
DesiKitchen/
  app.py
  models.py
  database.py
  requirements.txt
  README.md
  templates/
  static/
  database/desikitchen.db
```

## Main Modules

- Register, login, logout, and password reset
- Dashboard with inventory count, low stock count, shopping count, and notifications
- Inventory CRUD with search
- Shopping list with purchased status
- Recipe add, view, and search
- Recipe recommendation using available inventory item names
- Profile name and password update

## Interview Explanation

The project follows a simple MVC style. Models are written in `models.py`, database setup is in `database.py`, routes and controller logic are in `app.py`, templates are in `templates`, and static files are in `static`. SQLite keeps the project easy to run locally, while SQLAlchemy keeps database operations beginner-friendly.
