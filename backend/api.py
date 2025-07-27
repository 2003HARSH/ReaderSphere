from flask import Blueprint, request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import login_user, login_required, current_user
from .models import User, Message
from .extensions import db
from datetime import datetime
import os
from werkzeug.utils import secure_filename

api = Blueprint('api', __name__)

UPLOAD_FOLDER = 'backend/static/profile_pics'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@api.route('/my_profile', methods=['GET'])
@login_required
def api_my_profile():
    # Serialize current user
    user_data = {
        'id': current_user.id,
        'username': current_user.username,
        'email': current_user.email,
        'first_name': current_user.first_name,
        'last_name': current_user.last_name,
        'dob': current_user.dob.isoformat() if current_user.dob else None,
        'bio': current_user.bio,
        'profile_pic': current_user.profile_pic,
    }

    # Serialize non-friends
    non_friends = get_non_friends()
    non_friends_data = [
        {
            'id': user.id,
            'username': user.username,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'profile_pic': user.profile_pic,
        } for user in non_friends
    ]

    # Serialize pending friend requests
    pending_requests = get_pending_friend_requests()
    pending_data = [
        {
            'id': fr.id,
            'sender_id': fr.sender.id,
            'sender_username': fr.sender.username,
            'sender_profile_pic': fr.sender.profile_pic,
            'timestamp': fr.timestamp.isoformat()
        } for fr in pending_requests
    ]

    return jsonify({
        'user': user_data,
        'non_friends': non_friends_data,
        'pending_requests': pending_data
    })

@api.route('/edit_profile', methods=['POST'])
@login_required
def api_edit_profile():
    new_username = request.form.get('username')
    new_bio = request.form.get('bio')
    new_password = request.form.get('password')
    conf_new_password = request.form.get('conf_password')
    file = request.files.get('profile_pic')
    dob = request.form.get('dob')

    if new_username:
        current_user.username = new_username
    if new_bio:
        current_user.bio = new_bio
    if new_password and conf_new_password and new_password == conf_new_password:
        current_user.password = generate_password_hash(new_password)
    if dob:
        current_user.dob = datetime.strptime(dob, '%Y-%m-%d').date()

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        current_user.profile_pic = filename
    db.session.commit()

    return jsonify({'status': 'success', 'message': 'Profile updated successfully'}), 200

# --- Authentication Endpoints ---

@api.route('/login', methods=['POST'])
def api_login():
    data = request.get_json()
    email_username = data.get('username')
    password = data.get('password')

    if not email_username or not password:
        return jsonify({'status': False, 'message': 'Username and password are required'}), 400

    if '@' in email_username:
        user = User.query.filter_by(email=email_username).first()
    else:
        user = User.query.filter_by(username=email_username).first()

    if user and check_password_hash(user.password, password):
        login_user(user, remember=True)
        session_id = request.cookies.get('session')
        return jsonify({'status': True, 'session_id': session_id, 'message': 'Login successful'}), 200
    else:
        return jsonify({'status': False, 'message': 'Invalid Credentials'}), 401

@api.route('/signup', methods=['POST'])
def api_signup():
    # This assumes form data is sent. If JSON, use request.get_json()
    data = request.form
    email = data.get('email')
    username = data.get('username')
    # ... (add all other fields from your signup form)

    # Basic validation
    if not email or not username:
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    # ... (add the comprehensive validation logic from your signup_util function)

    # Create new user
    new_user = User(
        email=email,
        username=username,
        # ... (initialize other fields)
        password=generate_password_hash(data.get('password'), method='pbkdf2:sha256')
    )
    db.session.add(new_user)
    db.session.commit()
    login_user(new_user, remember=True)
    session_id = request.cookies.get('session')

    return jsonify({'status': 'success', 'session_id': session_id, 'message': 'Signup successful'}), 201

# --- Messaging Endpoints ---

@api.route('/users/friends', methods=['GET'])
@login_required
def get_friends():
    users = current_user.friends
    users_data = [{
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'profile_pic': user.profile_pic
    } for user in users]
    return jsonify(users_data)

@api.route('/messages/<int:receiver_id>', methods=['GET'])
@login_required
def get_messages(receiver_id):
    messages = Message.query.filter(
        ((Message.sender_id == current_user.id) & (Message.receiver_id == receiver_id)) |
        ((Message.sender_id == receiver_id) & (Message.receiver_id == current_user.id))
    ).order_by(Message.timestamp).all()

    messages_data = [{
        'sender_id': message.sender_id,
        'sender_name': User.query.get(message.sender_id).first_name,
        'message': message.content,
        'timestamp': message.timestamp.strftime('%Y-%m-%d %H:%M:%S')
    } for message in messages]
    return jsonify(messages_data)