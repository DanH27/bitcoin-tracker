from cointrade import db, login_manager
from datetime import datetime
from flask_login import UserMixin


#Load current user
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#Make user model for the ORM
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)
    currency = db.relationship('Currency', backref='owner', lazy=True)
    admin = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}')"

#Create currency model for the ORM
class Currency(db.Model):
    __tablename__ = 'currency'
    id = db.Column(db.Integer, primary_key=True)
    btc = db.Column(db.Integer(), nullable=False, default=0)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    cash = db.Column(db.Integer, nullable=False, default=100000)

    def __repr__(self):
        return f"Currency('{self.btc}', '{self.date_posted}'"

#db.create_all()
