from flask import Blueprint,render_template,request,flash,redirect,url_for,jsonify
import os
from .models import User
from .extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_required,login_user,logout_user,current_user
from werkzeug.utils import secure_filename
import boto3
from botocore.exceptions import NoCredentialsError

# --- S3 Configuration ---
S3_BUCKET = os.getenv('S3_BUCKET_NAME')
S3_LOCATION = f'https://{S3_BUCKET}.s3.amazonaws.com/'
S3_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY_ID')
S3_SECRET_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')

def upload_to_s3(file, bucket_name, acl="public-read"):
    """
    Uploads a file object to an S3 bucket.
    """
    try:
        s3 = boto3.client(
           "s3",
           aws_access_key_id=S3_ACCESS_KEY,
           aws_secret_access_key=S3_SECRET_KEY
        )
        s3.upload_fileobj(
            file,
            bucket_name,
            file.filename,
            ExtraArgs={
                "ACL": acl,
                "ContentType": file.content_type
            }
        )
    except FileNotFoundError:
        print("The file was not found")
        return None
    except NoCredentialsError:
        print("Credentials not available")
        return None
    return f"{S3_LOCATION}{file.filename}"


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'avif'}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


def login_util(email_username,password,frontend):    
    is_authenticated=False
    if email_username.endswith('@gmail.com'):
        user=User.query.filter_by(email=email_username).first() 
    else:
        user=User.query.filter_by(username=email_username).first() 

    if user and check_password_hash(user.password,password):
        is_authenticated=True
        login_user(user,remember=True)

    if frontend=='web':
        if is_authenticated:
            flash("Logged In Successfully",category='success')
            return redirect(url_for('views.profile',username=user.username))
        else:
            flash('Incorect username or password',category='error')
            return render_template('login.html',user=current_user)        
    
    if frontend=='api':
        if is_authenticated :
            session_id = request.cookies.get('session')  
            return jsonify({'status': True,'session_id':session_id, 'message': 'Login successful'}), 200
        else:
            return jsonify({'status': False, 'message': 'Invalid Credentials'}), 401

def signup_util(request,frontend):

    email=request.form.get('email')
    username=request.form.get('username')
    first_name=request.form.get('first_name')
    last_name=request.form.get('last_name')
    dob=request.form.get('dob')
    password=request.form.get('password')
    confirm_password=request.form.get('confirm_password')
    file = request.files.get('profile_pic')

    DEFAULT_PROFILE_PIC_URL = os.getenv('DEFAULT_PROFILE_PIC_URL', 'https://readersphere.s3.ap-south-1.amazonaws.com/default.avif')
    profile_pic_url = DEFAULT_PROFILE_PIC_URL # Use the full URL as the default

    if file and allowed_file(file.filename):
        file.filename = secure_filename(file.filename)
        uploaded_url = upload_to_s3(file, S3_BUCKET)
        if uploaded_url:
              profile_pic_url = uploaded_url # Overwrite default only if upload succeeds

    msg=[]
    flag=True
    # --- (Your validation logic for email, username, etc. remains here) ---
    if User.query.filter_by(email=email).first():
        msg.append("Email already exists")
        flag=False
    if User.query.filter_by(username=username).first():
        msg.append("Username already exists")
        flag=False
    if not (email.endswith('@gmail.com') and email!='@gmail.com' and email[:-10].isalnum()):
        msg.append("Invalid email")
        flag=False
    if not(first_name.isalpha() and len(first_name)>2):
        msg.append("Invalid first_name")
        flag=False
    if not(last_name.isalpha() and len(last_name)>2):
        msg.append("Invalid last_name")
        flag=False
    if not(password==confirm_password):
        msg.append("Password don't Match")
        flag=False
    if not(len(password)>3):
        msg.append('Password too short , must be alteast 8 characters long')
        flag=False
    if not(int(dob.split('-')[0]) < 2012 and int(dob.split('-')[0]) > 1900):
        msg.append("Invalid DOB")
        flag=False
        
    if flag:
        user=User(email=email,username=username,first_name=first_name,last_name=last_name,password=generate_password_hash(password),dob=datetime.strptime(dob, '%Y-%m-%d').date(),profile_pic=profile_pic_url)
        db.session.add(user)
        db.session.commit()
        login_user(user,remember=True)
        if frontend=='web':
            flash("Account created",category='success')
            return redirect(url_for('views.my_profile'))
        elif frontend=='api':
            session_id = request.cookies.get('session')  
            return jsonify({'status': 'success', 'session_id':session_id,'message': 'Login successful'}), 200
    else:
        if frontend=='web':
            for i in msg:
                flash(i,category='error')
            return render_template('signup.html',user=current_user)
        elif frontend=='api':
            return jsonify({'status': 'error', 'message': 'Invalid Input'}), 401
        
def edit_profile_util(request,frontend):
    new_username = request.form.get('username')
    new_bio = request.form.get('bio')
    new_password = request.form.get('password')
    conf_new_password=request.form.get('conf_password')
    file = request.files.get('profile_pic')
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
        file.filename = secure_filename(file.filename)
        output_url = upload_to_s3(file, S3_BUCKET)
        if output_url:
            current_user.profile_pic = output_url 

    if frontend=='web':
        flash('Profile updated successfully!', category='success')
        return redirect(url_for('views.my_profile'))
    elif frontend=='api':
        return jsonify({'status': 'success', 'message': 'Profile updated successfully'}), 200
