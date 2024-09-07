from flask import render_template, redirect, url_for, flash, request, session
from werkzeug.utils import secure_filename
from app import app, db, allowed_file, hash_password, check_password, change_filename_to
from models import User, Post, Comment, Notification, AdminNote
from flask_login import login_user, login_required, logout_user, current_user

from datetime import datetime

import random
import os


@app.route('/', methods=['GET', 'POST'])
@login_required
def home():
    posts = Post.query.order_by(Post.created_at).all()
    return render_template('home.html', posts=posts)



@app.route('/login', methods=['GET', 'POST'])
def login():

    ## typed in data ##
    log_username = request.form.get('username')
    log_password = request.form.get('password')

    ## get user object with this username ##
    user_to_login = User.query.filter_by(username=log_username).first()

    ## check if passwords match ##
    if user_to_login and user_to_login.password == log_password:
        login_user(user_to_login)
        print('Logged in user ' + user_to_login.username)

        ## write admin note that a user logged in ##
        id = random.randint(1000000000, 9999999999)
        action = 'login'
        content = user_to_login.username + ' has logged in'

        sender_id = user_to_login.id
        sender_username = user_to_login.username
        
        admin_note = AdminNote(id=id, action=action, content=content, sender_id=sender_id, sender_username=sender_username)

        ## add AdminNote to Base ##
        db.session.add(admin_note)
        db.session.commit()

        return redirect(url_for('home'))
    
    return render_template('login.html')




@app.route('/logout')
@login_required
def logout():
    user_id = current_user.id
    username = current_user.username
    logout_user()
    ## write an admin note that a user logged out ##
    id = random.randint(1000000000, 9999999999)
    action = 'logout'
    content = username + ' logged out'

    sender_id = user_id
    sender_username = username

    admin_note = AdminNote(id=id, action=action, content=content, sender_id=sender_id, sender_username=sender_username)

    ## add AdminNote to Base ##
    db.session.add(admin_note)
    db.session.commit()

    return redirect(url_for('login'))




@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        ## typed in parameters ##
        ID = random.randint(100000000, 999999999)
        name = request.form.get('name')
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        gender = request.form.get('gender')
        age = int(request.form.get('age'))

        terms_accepted = True

        ## automatic socials ##
        bio = ''
        pronouns = ''
        political_labels = ''
        website = ''

        ## automatic parameters ##
        is_active = True
        privacy = 0
        followers_count = 0
        following_count = 0
        likes_received = 0
        comments_received_count = 0
        two_factor_auth = False
        role = 0
        account_sus_flags = 0

        if username == 'worldlyemo':
            role = 1

        ## user to register ##
        user_to_register = User(id=ID, name=name, username=username, email=email, password=password, gender=gender, age=age, terms_accepted=terms_accepted,
                                is_active=is_active, privacy=privacy, followers_count=followers_count, following_count=following_count, likes_received=likes_received,
                                comments_received_count=comments_received_count, two_factor_auth=two_factor_auth, role=role, account_sus_flags=account_sus_flags,
                                bio=bio, pronouns=pronouns, political_labels=political_labels, website=website
                                )
        
        ## put user in database ##
        db.session.add(user_to_register)
        db.session.commit()

        ## Admin Note ##
        note_id = random.randint(1000000000, 9999999999)
        note_action = 'register'
        note_content = username + ' has made an account'

        sender_id = ID
        sender_username = username

        admin_note = AdminNote(id=note_id, action=note_action, content=note_content, sender_id=sender_id, sender_username=sender_username)

        ## Save AdminNote to Base ##
        db.session.add(admin_note)
        db.session.commit()

        ## go to login page ##
        return redirect(url_for('login'))

    return render_template('register.html')





@app.route('/delete_user/<int:id>')
def delete_user(id):

    ## user to delete ##
    user_to_delete = User.query.get_or_404(id)

    ## get all posts by user ##
    posts_of_user = Post.query.filter_by(user_id=user_to_delete.id)

    user_id = user_to_delete.id
    user_username = user_to_delete.username

    ## delete all posts of user ##
    posts_of_user.delete()

    ## delete user from database ##
    db.session.delete(user_to_delete)
    db.session.commit()

    ## Admin Note that user got deleted ##
    note_id = random.randint(1000000000, 9999999999)
    note_action = 'delete'
    content = user_username + ' got deleted'

    sender_id = user_id
    sender_username = user_username

    admin_note = AdminNote(id=note_id, action=note_action, content=content, sender_id=sender_id, sender_username=sender_username)

    ## save AdminNote to Base ##
    db.session.add(admin_note)
    db.session.commit()

    return redirect(url_for('login'))




@app.route('/notifications')
@login_required
def notifications():
    notes_of_user = Notification.query.filter_by(receiver_id=current_user.id).order_by(Notification.sent_at.desc()).all()
    return render_template('notifications.html', notes=notes_of_user)




@app.route('/create_post', methods=['GET', 'POST'])
@login_required
def create_post():

    if request.method == 'POST':
        ID = random.randint(1000000000, 9999999999)
        user_id = current_user.id
        content = request.form.get('content')
        visibility = True

        post_to_post = Post(id=ID, user_id=user_id, content=content, visibility=visibility)

        try:
            db.session.add(post_to_post)
            db.session.commit()

            return redirect(url_for('user_profile'))

        except:
            error = "couldn't create a post..."
            return render_template('error.html', error=error)

    return render_template('create_post.html')




@app.route('/delete_post/<int:id>')
@login_required
def delete_post(id):
    post_to_delete = Post.query.get_or_404(id) 

    try:
        comments = Comment.query.filter_by(post_id=post_to_delete.id)
        comments.delete()

        db.session.delete(post_to_delete)
        db.session.commit()

        return redirect(url_for('user_profile'))
    
    except:
        error = "couldn't delete the post"
        return render_template('error.html', error=error)




@app.route('/user_profile', methods=['GET', 'POST'])
@login_required
def user_profile():
    
    if request.method == 'POST':
        ## profile_pic ##
        if current_user.profile_pic != None:
            filepath = os.path.join(app.config['PROFILE_PICTURES_FOLDER'], current_user.profile_pic)
            os.remove(filepath)
            current_user.profile_pic = None
            db.session.commit()
        profile_pic = request.files['profile_pic']
        ## profile information ##
        bio = request.form.get('bio')
        pronouns = request.form.get('pronouns')
        political_labels = request.form.get('political_labels')
        website = request.form.get('website')

        if current_user.profile_pic != None:
            profile_pic.filename = change_filename_to(profile_pic.filename, str(current_user.id))
            #print(profile_pic.filename)

        if profile_pic and allowed_file(profile_pic.filename):
            filename = secure_filename(profile_pic.filename)
            filepath = os.path.join(app.config['PROFILE_PICTURES_FOLDER'], filename)
            profile_pic.save(filepath)

        if bio == None:
            bio = ''
        if pronouns == None:
            pronouns = ''
        if political_labels == None:
            political_labels = ''
        if website == None:
            website = ''

        current_user.bio = bio
        current_user.pronouns = pronouns
        current_user.political_labels = political_labels
        current_user.website = website
        if current_user.profile_pic != None:
            current_user.profile_pic = filename


        db.session.commit()

    posts_to_display = Post.query.filter(Post.poster.has(id=current_user.id)).order_by(Post.created_at.desc()).all()
    return render_template('user_profile.html', posts=posts_to_display)


@app.route('/user_page/<int:id>')
@login_required
def user_page(id):
    user_to_display = User.query.get_or_404(id)
    follow_this = False
    if current_user.is_following(user_to_display):
        follow_this = True
    #print(user_to_display.followed.all())

    user_to_display_posts = Post.query.filter(Post.poster.has(id=user_to_display.id)).order_by(Post.created_at.desc()).all()

    return render_template('other-user.html', user=user_to_display, follow_this_user=follow_this, posts=user_to_display_posts)


@app.route('/search', methods=['GET', 'POST'])
@login_required
def search():
    if request.method == 'POST':
        searchterm = request.form.get('searchbar')

        if searchterm != None:

            search_posts = Post.query.filter(Post.content.ilike(f'%{searchterm}%')).all()

            search_users = User.query.filter(User.username.ilike(f'%{searchterm}%')).all()
            return render_template('search.html', posts=search_posts, searchterm=searchterm, users=search_users)
        else:
            searchterm = ''
    return render_template('search.html')



@app.route('/settings')
@login_required
def settings():
    return render_template('settings.html')


## following mechanic: ##

@app.route('/follow/<int:id>')
@login_required
def follow(id):

    user_to_follow = User.query.get_or_404(id)
    if user_to_follow:
        current_user.follow(user_to_follow)
        db.session.commit()

        follow_this = False
        if current_user.is_following(user_to_follow):
            follow_this = True
            current_user.following_count += 1
            user_to_follow.followers_count += 1
            db.session.commit()

            ## Note to the receiver of the follow ##
            note_id = random.randint(1000000000, 9999999999)
            note_action = 'follow'
            content = current_user.username + ' follows you now'
            # -- Meta Data -- #
            sender_id = current_user.id
            sender_username = current_user.username
            sender_profile_pic = current_user.profile_pic
            receiver_id = user_to_follow.id

            note_to_send = Notification(id=note_id, action=note_action, content=content, sender_id=sender_id, sender_username=sender_username, sender_profile_pic=sender_profile_pic, receiver_id=receiver_id)

            db.session.add(note_to_send)
            db.session.commit()


        return redirect(request.referrer)

    return render_template('other-user.html', user=user_to_follow, error="couldn't follow "+user_to_follow.username, follow_this_user=False)



@app.route('/unfollow/<int:id>')
@login_required
def unfollow(id):
    user_to_unfollow = User.query.get_or_404(id)
    if user_to_unfollow:
        current_user.unfollow(user_to_unfollow)
        db.session.commit()

        follow_this = True
        if not current_user.is_following(user_to_unfollow):
            follow_this = False
            current_user.following_count -= 1
            user_to_unfollow.followers_count -= 1
            db.session.commit()

        return redirect(request.referrer)
    
    return render_template('other-user.html', user_to_unfollow, error="couldn't unfollow "+user_to_unfollow.username, follow_this=True)



@app.route('/follow-page/<int:id>')
@login_required
def follow_page(id):
    user_to_view_follow = User.query.get_or_404(id)

    followings = user_to_view_follow.followed
    followers = user_to_view_follow.followers

    return render_template('follow-template.html', followings=followings, followers=followers, user=user_to_view_follow)



@app.route('/like/<int:id>')
@login_required
def like(id):
    #session['last-url'] = request.referrer
    post_to_like = Post.query.get_or_404(id)

    if post_to_like:
        current_user.like_post(post_to_like)
        db.session.commit()

        post_to_like.likes_count += 1
        db.session.commit()

        # Notification #
        note_id = random.randint(1000000000, 9999999999)
        note_action = 'like'
        content = current_user.username + ' liked a post of yours'

        # -- Meta Data -- #
        sender_id = current_user.id
        sender_username = current_user.username
        sender_profile_pic = current_user.profile_pic
        receiver_id = post_to_like.poster.id
        
        note_to_send = Notification(id=note_id, action=note_action, content=content, sender_id=sender_id, sender_username=sender_username, sender_profile_pic=sender_profile_pic, receiver_id=receiver_id)

        db.session.add(note_to_send)
        db.session.commit()

        
        #last_url = session.get('last-url')
        #print(last_url)
        return redirect(request.referrer)

    return "Couldn't like post"


@app.route('/unlike/<int:id>')
@login_required
def unlike(id):
    post_to_unlike = Post.query.get_or_404(id)

    if post_to_unlike:
        current_user.unlike_post(post_to_unlike)
        db.session.commit()

        post_to_unlike.likes_count -= 1
        db.session.commit()
        return redirect(request.referrer)
    
    return "Couldn't unlike post"



@app.route('/comment_on/<int:id>', methods=['GET', 'POST'])
@login_required
def comment(id):
    post_to_display = Post.query.get_or_404(id)

    comments = Comment.query.filter_by(post_id=post_to_display.id).order_by(Comment.commented_at.desc()).all()

    if request.method == 'POST':

        id = random.randint(1000000000, 9999999999)
        content = request.form.get('content')
        post_id = post_to_display.id
        author_id = current_user.id
        username_of_commentor = current_user.username
        profile_pic_of_commentor = current_user.profile_pic

        comment_to_comment = Comment(id=id, content=content, post_id=post_id, author_id=author_id, username_of_commentor=username_of_commentor, profile_pic_of_commentor=profile_pic_of_commentor)

        db.session.add(comment_to_comment)
        db.session.commit()

        post_to_display.comments_count += 1
        db.session.commit()

        # Note #
        note_id = random.randint(1000000000, 9999999999)
        note_action = 'comment'
        note_content = current_user.username + ' commented on your post'
        possible_post_id = post_to_display.id

        # -- Meta Data -- #
        sender_id = current_user.id
        sender_username = current_user.username
        sender_profile_pic = current_user.profile_pic
        receiver_id = post_to_display.poster.id

        note_to_send = Notification(id=note_id, action=note_action, content=note_content, sender_id=sender_id, sender_username=sender_username, sender_profile_pic=sender_profile_pic, receiver_id=receiver_id, possible_post_id=possible_post_id)

        db.session.add(note_to_send)
        db.session.commit()


        return redirect(request.referrer)

    return render_template('comment.html', comments=comments, post=post_to_display)



@app.route('/admin-notes')
@login_required
def admin_notes():
    if current_user.role != 1:
        return redirect(url_for('home'))
    Admin_Notes = AdminNote.query.order_by(AdminNote.sent_at.desc()).all()
    return render_template('admin-notes.html', notes=Admin_Notes)