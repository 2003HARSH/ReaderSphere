from flask import Blueprint,render_template,request,jsonify,redirect,url_for
from flask_login import login_required,current_user
from .models import User,Message
from .extensions import socketio,db

views=Blueprint('views',__name__)

@views.route('/')
def index():
    if current_user:
        return redirect(url_for('views.profile'))
    return(redirect(url_for('auth.login')))

@views.route('/profile')
@login_required
def profile():
    return render_template('profile.html',user=current_user,people=User.query.all()) #temporary

@views.route('/messages')
@login_required
def messages():
    return render_template('messages.html', user=current_user)

@views.route('/get_users')
@login_required
def get_users():
    # Fetch all users except the current user
    users = User.query.filter(User.id != current_user.id).all()

    # Convert users to a list of dictionaries
    users_data = [{
        'id': user.id,
        'username':user.username,
        'first_name': user.first_name,
        'profile_pic':user.profile_pic
    } for user in users]

    return jsonify(users_data)

@views.route('/get_messages/<int:receiver_id>')
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

