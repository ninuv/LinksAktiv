import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

from datetime import datetime

import bcrypt



# app #
app = Flask(__name__)


# configuration #
app.config['SECRET_KEY'] = 'Your secret key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///left.db'

app.config['PROFILE_PICTURES_FOLDER'] = os.path.join('static', 'profile_pictures')
app.config['ALLOWED_EXTENSIONS'] = {
    'png', 'jpg', 'jpeg', 'gif',   ## Image Formatting ##
    #'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv'   ## Video Formatting ##
    }



# create upload dir, if it doesn't exist #
if not os.path.exists(app.config['PROFILE_PICTURES_FOLDER']):
    os.makedirs(app.config['PROFILE_PICTURES_FOLDER'])



# check if file is allowed #
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']



# hashing password #
def hash_password(password: str) -> str:
    
    #generate salt
    salt = bcrypt.gensalt()

    #hash the password
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)

    #return password hashed as a string
    return hashed.decode('utf-8')



# checking hashed password #
def check_password(password: str, hashed_password: str) -> bool:
    #check if password and hashed password match
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))



# changing filename to user_id . filetype
def change_filename_to(oldfilename, partbeforedot):
    datatype = oldfilename.split(".")[1]
    new_filename = partbeforedot + '.' + datatype
    return new_filename


# isolate filetype
def isolate_filetype(filename):
    datatype = filename.split(".")[1]
    return datatype


# db #
db = SQLAlchemy(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'



# importing routes and models #
from routes import *
from models import *



# run application #
if __name__ == '__main__':
    app.run(debug=True)