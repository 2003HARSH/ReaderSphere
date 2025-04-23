from flask import Flask
from os import path
import os
from .sockets import configure_socketio
from flask_migrate import Migrate

def create_app():
    from .extensions import socketio,db,login_manager,DB_NAME
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    db.init_app(app)

    migrate = Migrate(app, db)
    socketio.init_app(app, cors_allowed_origins="*")

    from .views import views
    from .auth import auth

    app.register_blueprint(views, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from . import models  # Run it once
    login_manager.login_view='auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return models.User.query.get(int(id))

    if not path.exists("backend/" + DB_NAME):
        with app.app_context():
            db.create_all()
            print("Database created")
    
    configure_socketio(socketio)


    return app,socketio

           
