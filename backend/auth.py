from flask import Blueprint,render_template,request,redirect,url_for
from .utils import login_util,signup_util,edit_profile_util
from flask_login import login_required,login_user,logout_user,current_user

auth=Blueprint('auth',__name__)


@auth.route('/login',methods=['GET','POST'])
def login():
    if request.method=='GET':
        return render_template('login.html',user=current_user)
        
    elif request.method=='POST':
        email_username=request.form.get('email')
        password=request.form.get('password')
        return login_util(email_username,password,'web')
    
@auth.route('/logout')
@login_required
def logout():
    logout_user() 
    return redirect(url_for('auth.login'))

@auth.route('/signup',methods=['GET','POST'])
def signup():
    if request.method=='GET':
        return render_template('signup.html',user=current_user)
    
    elif request.method=='POST':
        return signup_util(request,frontend='web')
   
@auth.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'GET':
        return render_template('edit_profile.html', user=current_user)

    elif request.method=='POST':
        return edit_profile_util(request,frontend='web')
            
