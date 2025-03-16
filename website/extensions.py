from flask_socketio import SocketIO
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
import os
from dotenv import load_dotenv


load_dotenv()


db = SQLAlchemy()
DB_NAME=os.getenv('DB_NAME')
login_manager=LoginManager()
socketio=SocketIO()
