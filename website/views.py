from flask import Blueprint,render_template,request
from flask_login import login_required,current_user
from .models import User,Message
from .extensions import socketio,db

views=Blueprint('views',__name__)

@views.route('/')
def index():
    return render_template('index.html',user=current_user)

@views.route('/about')
def about():
    return render_template('about.html',user=current_user)

@views.route('/profile')
@login_required
def profile():
    return render_template('profile.html',user=current_user,friends=User.query.all()) #temporary

@views.route('/messages')
@login_required
def messages():
    previous_messages = Message.query.order_by(Message.timestamp).all()

    messages_data = [{
        'firstname': User.query.filter_by(id=message.sender_id).first().first_name,  
        'message': message.content,
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for message in previous_messages]

    return render_template('messages.html', user=current_user, messages=messages_data)