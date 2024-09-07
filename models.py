from datetime import datetime, timezone
from app import db, app, login_manager, hash_password
from flask_login import UserMixin

import json



user_follow_table = db.Table('user_follow_table',
    db.Column('follower_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('user.id'))
)

likes_table = db.Table('likes_table',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'))
)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), nullable=False)

    gender = db.Column(db.String(150), nullable=False)
    pronouns = db.Column(db.String(150), nullable=True)
    age = db.Column(db.Integer, nullable=False)
    bio = db.Column(db.String(300), nullable=True)
    profile_pic = db.Column(db.String(200), nullable=True)

    website = db.Column(db.String(200), nullable=True)
    political_labels = db.Column(db.String(200), nullable=True)

    # language setting state
    lang = db.Column(db.String(10), default='eng')

    # privacy: 0 = public -- 1 = private -- 2 = restricted etc.
    is_active = db.Column(db.Boolean, default=True)
    privacy = db.Column(db.Integer, default=0)

    followers_count = db.Column(db.Integer, default=0)
    following_count = db.Column(db.Integer, default=0)

    followed = db.relationship('User', secondary=user_follow_table, backref='followers',
                               secondaryjoin=(user_follow_table.c.followed_id == id),
                               primaryjoin=(user_follow_table.c.follower_id == id), lazy='dynamic'
                               )

    likes_received = db.Column(db.Integer, default=0)
    comments_received_count = db.Column(db.Integer, default=0)

    # groups joined =

    # roles: 0 = standard_user -- 1 = ...
    two_factor_auth = db.Column(db.Boolean, default=False)
    role = db.Column(db.Integer, default=0)
    account_sus_flags = db.Column(db.Integer, default=0)
    # terms_accepted_at
    terms_accepted = db.Column(db.Boolean, default=False)
    # posts of the user -- use 'poster' if you reference the author of the post THROUGH the post.. i.e. 'post.poster.id'
    posts = db.relationship('Post', backref='poster')
    # liked posts
    liked_posts = db.relationship('Post', secondary=likes_table, backref='liker')

    ## comments that this user left: ##
    comments = db.relationship('Comment', backref='author', lazy=True)


    ## follow mechanic inside user class: user. ... ##
    
    # follow a user:
    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    # unfollow a user:
    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    # check if user is following: (returns bool) [inner usage]
    def is_following(self, user):
        return self.followed.filter(user_follow_table.c.followed_id == user.id).count() > 0
    

    ## like mechanic inside user class: user. ... ##

    # like a post:
    def like_post(self, post):
        if not self.has_liked_post(post):
            self.liked_posts.append(post)

    # unlike a post:
    def unlike_post(self, post):
        if self.has_liked_post(post):
            self.liked_posts.remove(post)

    # check if user liked post: [inner usage]
    def has_liked_post(self, post):
        return post in self.liked_posts



class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    visibility = db.Column(db.Boolean, default=True)
    likes_count = db.Column(db.Integer, default=0)

    ## comments that users left ##
    comments = db.relationship('Comment', backref='post', lazy=True)
    comments_count = db.Column(db.Integer, default=0)



# nuanced Notification System
class Notification(db.Model): # singular Notification
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(200), nullable=True)
    possible_post_id = db.Column(db.Integer, nullable=True)

    ## Meta Data ##
    sender_id = db.Column(db.Integer, nullable=False)
    sender_username = db.Column(db.String(200), nullable=False)
    sender_profile_pic = db.Column(db.String(200))
    receiver_id = db.Column(db.Integer, nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.now)




class AdminNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    action = db.Column(db.String(100), nullable=False)
    content = db.Column(db.String(200), nullable=True)

    # -- Meta Data -- #
    sender_id = db.Column(db.Integer, nullable=False)
    sender_username = db.Column(db.String(200), nullable=False)
    sent_at = db.Column(db.DateTime, default=datetime.now)






class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'))
    content = db.Column(db.Text, nullable=False)
    commented_at = db.Column(db.DateTime, default=datetime.now)
    username_of_commentor = db.Column(db.String(200))
    profile_pic_of_commentor = db.Column(db.String(200))




@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

with app.app_context():
    db.create_all()