from flask import Blueprint,render_template
from flask_login import login_required,current_user

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
    return render_template('profile.html',user=current_user)