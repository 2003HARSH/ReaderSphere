from flask import Blueprint,render_template,request,jsonify,redirect,url_for,abort
from flask_login import login_required,current_user
from .models import User,Message,FriendRequest,BookRating
import requests
from bs4 import BeautifulSoup
from .extensions import db
from sqlalchemy import func

group_manager=Blueprint('group_manager',__name__)


@group_manager.route('/groups')
@login_required
def groups():
    my_groups = current_user.groups
    
    # Create a dictionary to hold non-member friends for each group
    non_member_friends_by_group = {}
    for group in my_groups:
        if group.created_by_id == current_user.id:
            group_members_ids = {member.id for member in group.members}
            non_member_friends = [
                friend for friend in current_user.friends if friend.id not in group_members_ids
            ]
            non_member_friends_by_group[group.id] = non_member_friends

    return render_template('groups.html', 
                           user=current_user, 
                           groups=my_groups, 
                           non_member_friends_by_group=non_member_friends_by_group)
