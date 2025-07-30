from flask import Blueprint,render_template,request,jsonify,redirect,url_for,abort
from flask_login import login_required,current_user
from .models import User,Message,FriendRequest
import requests
from bs4 import BeautifulSoup

views=Blueprint('views',__name__)

@views.route('/')
def index():
    if current_user:
        return redirect(url_for('views.my_profile'))
    return(redirect(url_for('auth.login')))

@views.route('/<username>')
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
        return redirect(url_for('views.my_profile'))
    
@views.route('/my_profile')
@login_required
def my_profile():
    people=User.query.filter(User.id!=current_user.id).all()
    pending_requests = FriendRequest.query.filter_by(receiver_id=current_user.id, status='pending').all()
    non_friends = User.query.filter(User.id != current_user.id).filter(~User.id.in_([friend.id for friend in current_user.friends])).all()
    return render_template('profile.html', user=current_user, people=non_friends, edit=True, pending_requests=pending_requests)


@views.route('/messages')
@login_required
def messages():
    return render_template('messages.html', user=current_user)

@views.route('/get_users')
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


@views.route('/books')
@login_required
def books():
    return render_template('books.html',user=current_user)

@views.route('/book/<title>')
@login_required
def book(title):
    url = f"https://www.googleapis.com/books/v1/volumes/{title}"
    res = requests.get(url)
    data = res.json()

    info = data.get('volumeInfo', {})
    Title= info.get("title")
    Authors=info.get("authors")
    Publisher=info.get("publisher")
    Category=info.get("categories")
    pageCount=info.get("pageCount")
    Description=info.get("description")
    Description=BeautifulSoup(Description, "html.parser").get_text()
    Thumbnail=info.get("imageLinks", {}).get("thumbnail")
    return render_template("book_detail.html",user=current_user,
                           Title=Title,
                           Authors=Authors,
                           Publisher=Publisher,
                           Category=Category,
                           pageCount=pageCount,
                           Description=Description,
                           Thumbnail=Thumbnail)

@views.route('/book/search/<query>')
@login_required
def book_search(query):
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}"
    res = requests.get(url)
    data = res.json()

    for book in data['items'][:1]:
        info = book['volumeInfo']
        Title= info.get("title")
        Authors=info.get("authors")
        Publisher=info.get("publisher")
        Category=info.get("categories")
        pageCount=info.get("pageCount")
        Description=info.get("description")
        Description=BeautifulSoup(Description, "html.parser").get_text()
        Thumbnail=info.get("imageLinks", {}).get("thumbnail")
    return render_template("book_detail.html",user=current_user,
                           Title=Title,
                           Authors=Authors,
                           Publisher=Publisher,
                           Category=Category,
                           pageCount=pageCount,
                           Description=Description,
                           Thumbnail=Thumbnail)


@views.route('/groups')
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