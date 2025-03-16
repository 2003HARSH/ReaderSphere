from flask import Blueprint,render_template,request,flash,redirect,url_for
import string
from .models import User
from .extensions import db
from datetime import datetime
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_required,login_user,logout_user,current_user

auth=Blueprint('auth',__name__)

@auth.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html',user=current_user)
    elif request.method=='POST':
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first() #we get a row
        if user:
            if check_password_hash(user.password,password):
                flash("Logged In Successfully",category='success')
                login_user(user,remember=True)
                return redirect(url_for('views.profile'))
            else:
                flash('Incorect username or password',category='error')
                return render_template('login.html')
        flash('No user found with this email',category='error')
        return render_template('login.html',current_user=user)

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
        first_name=request.form.get('first_name')
        last_name=request.form.get('last_name')
        dob=request.form.get('dob')
        password=request.form.get('password')
        confirm_password=request.form.get('confirm_password')

        flag=True

        user=User.query.filter_by(email=email).first() #we get a row

        if user:
            flash("Email already exists",category='error')
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
            user=User(email=email,first_name=first_name,last_name=last_name,password=generate_password_hash(password),dob=datetime.strptime(dob, '%Y-%m-%d').date())
            db.session.add(user)
            db.session.commit()
            flash("Account created",category='success')
            login_user(user,remember=True)
            return redirect(url_for('views.profile'))

        return render_template('signup.html',user=current_user)
        
        