import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from .models import db, User
from .routes import main

login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

def create_app():
    app = Flask(__name__, instance_relative_config=True)
    os.makedirs(app.instance_path, exist_ok=True)
    app.config.update(
        SECRET_KEY=os.getenv("SECRET_KEY", "development-only-change-me"),
        SQLALCHEMY_DATABASE_URI=os.getenv("DATABASE_URL", "sqlite:///" + os.path.join(app.instance_path, "swingdesk.db")),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SAMESITE="Lax",
        SESSION_COOKIE_SECURE=os.getenv("COOKIE_SECURE", "0") == "1",
        MAX_CONTENT_LENGTH=5 * 1024 * 1024,
    )
    from flask_sqlalchemy import SQLAlchemy
    # SQLAlchemy extension is initialised in models.py
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login"
    app.register_blueprint(main)
    with app.app_context():
        db.create_all()
    return app
