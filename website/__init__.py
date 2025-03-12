from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from dotenv import load_dotenv

db = SQLAlchemy()
DB_NAME=load_dotenv('DB_NAME')

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = load_dotenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from . import models  # Run it once
    login_manager=LoginManager()
    login_manager.login_view='auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return models.User.query.get(int(id))

    if not path.exists("website/" + DB_NAME):
        with app.app_context():
            db.create_all()
            print("Database created")

    return app

           
