from .extensions import db
from flask_login import UserMixin
import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    profile_pic = db.Column(db.String(120))
    password = db.Column(db.String(255), nullable=False)
    bio = db.Column(db.Text, nullable=True)  

class Message(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    sender_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    receiver_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    content=db.Column(db.String(1000),nullable=False)
    timestamp=db.Column(db.DateTime,default=datetime.datetime.utcnow)
    seen=db.Column(db.Boolean,default=False)