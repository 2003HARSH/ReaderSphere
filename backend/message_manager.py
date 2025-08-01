from flask import Blueprint,render_template,request,jsonify,redirect,url_for,abort
from flask_login import login_required,current_user
from .models import User,Message,FriendRequest,BookRating
import requests
from bs4 import BeautifulSoup
from .extensions import db
from sqlalchemy import func

message_manager=Blueprint('message_manager',__name__)

@message_manager.route('/messages')
@login_required
def messages():
    return render_template('messages.html', user=current_user)

@message_manager.route('/get_messages/<int:receiver_id>')
@login_required
def get_messages(receiver_id):
    # Fetch messages between the current user and the selected user
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == receiver_id)) |
        ((Message.sender_id == receiver_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp).all()

    # Convert messages to a list of dictionaries
    messages_data = [{
        'sender_id': message.sender_id,
        'sender_name': User.query.filter_by(id=message.sender_id).first().first_name,
        'message': message.content,
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for message in messages]

    return jsonify(messages_data)
