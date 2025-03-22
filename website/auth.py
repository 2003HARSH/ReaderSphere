from flask import Blueprint,render_template,request,flash,redirect,url_for
import os
from .models import User
from .extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_required,login_user,logout_user,current_user
from werkzeug.utils import secure_filename

auth=Blueprint('auth',__name__)


UPLOAD_FOLDER = 'website/static/profile_pics'  # Store uploaded images
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure the upload directory exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'avif'}


@auth.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html',user=current_user)
    elif request.method=='POST':
        email_username=request.form.get('email')
        if email_username.endswith('@gmail.com'):
            user=User.query.filter_by(email=email_username).first() #we get a row
        else:
            user=User.query.filter_by(username=email_username).first() #we get a row
        password=request.form.get('password')
        if user:
            if check_password_hash(user.password,password):
                flash("Logged In Successfully",category='success')
                login_user(user,remember=True)
                return redirect(url_for('views.profile',username=user.username))
            else:
                flash('Incorect username or password',category='error')
                return render_template('login.html')
        flash('No user found with this email or username',category='error')
        return render_template('login.html',user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user() #logouts the current user
    return redirect(url_for('auth.login'))

@auth.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='GET':
        return render_template('signup.html',user=current_user)
    elif request.method=='POST':
        email=request.form.get('email')
        username=request.form.get('username')
        first_name=request.form.get('first_name')
        last_name=request.form.get('last_name')
        dob=request.form.get('dob')
        password=request.form.get('password')
        confirm_password=request.form.get('confirm_password')

        # Handle profile picture upload
        file = request.files['profile_pic']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
        else:
            filename = 'default.avif'  # Use a default profile picture if none uploaded

        flag=True

        if User.query.filter_by(email=email).first():
            flash("Email already exists",category='error')
            flag=False
        if User.query.filter_by(username=username).first():
            flash("Username already exists",category='error')
            flag=False
        if not (email.endswith('@gmail.com') and email!='@gmail.com' and email[:-10].isalnum()):
            flash("Invalid email",category='error')
            flag=False
        if not(first_name.isalpha() and len(first_name)>2):
            flash("Invalid first_name",category='error')
            flag=False
        if not(last_name.isalpha() and len(last_name)>2):
            flash("Invalid last_name",category='error')
            flag=False
        if not(password==confirm_password):
            flash("Password don't Match",category='error')
            flag=False
        if not(len(password)>3):
            flash('Password too short , must be alteast 8 characters long')
            flag=False
        if not(int(dob.split('-')[0]) < 2012 and int(dob.split('-')[0]) > 1900):
            flash("Invalid DOB",category='error')
            flag=False
        if flag:
            user=User(email=email,username=username,first_name=first_name,last_name=last_name,password=generate_password_hash(password),dob=datetime.strptime(dob, '%Y-%m-%d').date(),profile_pic=filename)
            db.session.add(user)
            db.session.commit()
            flash("Account created",category='success')
            login_user(user,remember=True)
            return redirect(url_for('views.profile'))

        return render_template('signup.html',user=current_user)
    
@auth.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_bio = request.form.get('bio')
        new_password = request.form.get('password')
        conf_new_password=request.form.get('conf_password')
        file = request.files['profile_pic']
        dob=request.form.get('dob')

        if new_username:
            current_user.username = new_username
        if new_bio:
            current_user.bio = new_bio  
        if new_password and conf_new_password and new_password==conf_new_password:
            current_user.password = generate_password_hash(new_password)
        if dob:
            current_user.dob=datetime.strptime(dob, '%Y-%m-%d').date()


        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            current_user.profile_pic=filename

        db.session.commit()
        flash('Profile updated successfully!', category='success')
        return redirect(url_for('views.profile', username=current_user.username))

    return render_template('edit_profile.html', user=current_user)
        
        