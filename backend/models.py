from .extensions import db
from flask_login import UserMixin
import datetime

# Many-to-Many relationship for accepted friendships
friends_association = db.Table('friends',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('friend_id', db.Integer, db.ForeignKey('user.id'))
)

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    password = db.Column(db.String(200))
    dob = db.Column(db.Date)
    profile_pic = db.Column(db.String(200))
    bio = db.Column(db.Text)

    # Many-to-Many: confirmed friends
    friends = db.relationship(
        'User',
        secondary=friends_association,
        primaryjoin=id == friends_association.c.user_id,
        secondaryjoin=id == friends_association.c.friend_id,
        backref='friend_of'
    )

    def is_friend(self, other_user):
        return other_user in self.friends


class FriendRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    receiver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # 'pending', 'accepted', 'rejected'

    sender = db.relationship('User', foreign_keys=[sender_id], backref='sent_friend_requests')
    receiver = db.relationship('User', foreign_keys=[receiver_id], backref='received_friend_requests')

    def is_pending(self):
        return self.status == 'pending'

    def is_accepted(self):
        return self.status == 'accepted'

class Message(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    sender_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    receiver_id=db.Column(db.Integer,db.ForeignKey('user.id'),nullable=False)
    content=db.Column(db.String(1000),nullable=False)
    timestamp=db.Column(db.DateTime,default=datetime.datetime.utcnow)
    seen=db.Column(db.Boolean,default=False)


group_members = db.Table('group_members',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
)

class Group(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_by_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_by = db.relationship('User', backref='created_groups')
    members = db.relationship('User', secondary=group_members, backref='groups')

class GroupMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(1000), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    group = db.relationship('Group', backref='messages')
    sender = db.relationship('User')