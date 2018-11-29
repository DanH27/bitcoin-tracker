from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
#import os

#Set debugging to True or False
#debugging = True

app = Flask(__name__)

app.config['SECRET_KEY'] = 'f9fc238959f76fa032a7294936fcd953'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'

# if debugging:
#     app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:root@localhost/bitrade'
# else:
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://zwtwfqpmhdollx:1be6ad4b2beae0b622f17a3639d3b107cdf00b63bb07320f274d37a8f5129dc8@ec2-54-225-110-156.compute-1.amazonaws.com:5432/dbj879b1ua6pgk'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

from cointrade import routes
