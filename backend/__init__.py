from flask import Flask
from os import path
import os
from .sockets import configure_socketio
from flask_migrate import Migrate
from flask_cors import CORS

def create_app():
    from .extensions import socketio,db,login_manager
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": "*"}}) 
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


    database_url = os.getenv('DATABASE_URL')
    if database_url:
        if database_url.startswith("postgres://"):
            database_url = database_url.replace("postgres://", "postgresql://", 1)
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    else:
        db_user = os.getenv('DB_USER')
        db_password = os.getenv('DB_PASSWORD')

    db.init_app(app)

    migrate = Migrate(app, db)
    socketio.init_app(app, cors_allowed_origins="*")

    from .views import views
    from .auth import auth
    from .api import api 

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(api, url_prefix='/api/v1')

    from . import models
    login_manager.login_view='auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return models.User.query.get(int(id))

    configure_socketio(socketio)

    return app,socketio