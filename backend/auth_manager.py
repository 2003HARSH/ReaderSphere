from flask import Blueprint,render_template,request,redirect,url_for,flash
from .utils import S3_BUCKET,allowed_file,upload_to_s3
from flask_login import login_required,login_user,logout_user,current_user
from werkzeug.utils import secure_filename
from .models import User
from werkzeug.security import generate_password_hash,check_password_hash
import os
from .extensions import db
from datetime import datetime

auth_manager=Blueprint('auth_manager',__name__)

DEFAULT_PROFILE_PIC_URL = os.getenv('DEFAULT_PROFILE_PIC_URL')


@auth_manager.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html',user=current_user)
        
    elif request.method=='POST':
        email_username=request.form.get('email')
        password=request.form.get('password')
        is_authenticated=False
        if email_username.endswith('@gmail.com'):
            user=User.query.filter_by(email=email_username).first() 
        else:
            user=User.query.filter_by(username=email_username).first() 

        if user and check_password_hash(user.password,password):
            is_authenticated=True
            login_user(user,remember=True)

        if is_authenticated:
            flash("Logged In Successfully",category='success')
            return redirect(url_for('profile_manager.profile',username=user.username))
        else:
            flash('Incorect username or password',category='error')
            return render_template('login.html',user=current_user) 
                
@auth_manager.route('/logout')
@login_required
def logout():
    logout_user() 
    return redirect(url_for('auth_manager.login'))

@auth_manager.route('/signup',methods=['GET','POST'])
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
        file = request.files.get('profile_pic')

        profile_pic_url = DEFAULT_PROFILE_PIC_URL # Use the full URL as the default

        if file and allowed_file(file.filename):
            file.filename = secure_filename(file.filename)
            uploaded_url = upload_to_s3(file, S3_BUCKET)
            if uploaded_url:
                  profile_pic_url = uploaded_url # Overwrite default only if upload succeeds

        msg=[]
        flag=True
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
            flash("Account created",category='success')
            return redirect(url_for('profile_manager.my_profile'))
        else:
            for i in msg:
                flash(i,category='error')
            return render_template('signup.html',user=current_user)

        
