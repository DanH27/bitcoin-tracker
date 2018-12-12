from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
#import os

#Set debugging to True or False
debugging = False

app = Flask(__name__)

app.config['SECRET_KEY'] = 'f9fc238959f76fa032a7294936fcd953'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

if debugging:
     app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/bitrade'
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://teopiqfwhkgadm:b39ab93fd66a7c02bf68417cc1dc62d67ed9fb1b68b51939908978c2f12bc11a@ec2-54-163-245-64.compute-1.amazonaws.com:5432/d72h6r5qn3sd0'
#Make a db object using SQLAlchemy
db = SQLAlchemy(app)
#Make a bcrypt object
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from cointrade import routes
