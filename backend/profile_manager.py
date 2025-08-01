from flask import Blueprint,render_template,request,redirect,url_for,flash
from .utils import upload_to_s3,allowed_file,S3_BUCKET
from werkzeug.utils import secure_filename
from flask_login import login_required,current_user
from flask import Blueprint,render_template,request,jsonify,redirect,url_for,abort
from .models import User,FriendRequest
from .extensions import db
from werkzeug.security import generate_password_hash
from datetime import datetime


profile_manager=Blueprint('profile_manager',__name__)
   
    
@profile_manager.route('/')
def index():
    if current_user:
        return redirect(url_for('profile_manager.my_profile'))
    return(redirect(url_for('auth_manager.login')))

@profile_manager.route('/<username>')
@login_required
def profile(username):
    if username != current_user.username:
        user=User.query.filter_by(username=username).first()

        if user is None:
            abort(404) 

        is_friend = False
        if user in current_user.friends:
            is_friend = True
        return render_template('profile.html',user=user,is_friend=is_friend,edit=False)
    else:
        return redirect(url_for('profile_manager.my_profile'))
    
@profile_manager.route('/my_profile')
@login_required
def my_profile():
    people=User.query.filter(User.id!=current_user.id).all()
    pending_requests = FriendRequest.query.filter_by(receiver_id=current_user.id, status='pending').all()
    non_friends = User.query.filter(User.id != current_user.id).filter(~User.id.in_([friend.id for friend in current_user.friends])).all()
    return render_template('profile.html', user=current_user, people=non_friends, edit=True, pending_requests=pending_requests)

@profile_manager.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'GET':
        return render_template('edit_profile.html', user=current_user)

    elif request.method=='POST':
        new_username = request.form.get('username')
        first_name=request.form.get('first_name')
        last_name=request.form.get('last_name')
        new_bio = request.form.get('bio')
        new_password = request.form.get('password')
        conf_new_password=request.form.get('conf_password')
        file = request.files.get('profile_pic')
        dob=request.form.get('dob')

        if new_username:
            current_user.username = new_username
        if first_name:
            current_user.first_name = first_name
        if last_name:
            current_user.last_name = last_name
        if new_bio:
            current_user.bio = new_bio  
        if new_password and conf_new_password and new_password==conf_new_password:
            current_user.password = generate_password_hash(new_password)
        if dob:
            current_user.dob=datetime.strptime(dob, '%Y-%m-%d').date()

        if file and allowed_file(file.filename):
            file.filename = secure_filename(file.filename)
            output_url = upload_to_s3(file, S3_BUCKET)
            if output_url:
                current_user.profile_pic = output_url 

        db.session.commit()

        flash('Profile updated successfully!', category='success')
        return redirect(url_for('profile_manager.my_profile'))

    
@profile_manager.route('/get_users')
@login_required
def get_users():
    # Fetch all users except the current user
    users = current_user.friends

    # Convert users to a list of dictionaries
    users_data = [{
        'id': user.id,
        'username':user.username,
        'first_name': user.first_name,
        'profile_pic':user.profile_pic
    } for user in users]

    return jsonify(users_data)
            
