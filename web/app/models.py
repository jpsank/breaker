from app import db, login
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy import func, or_, and_
from flask_login import UserMixin, current_user
from werkzeug.security import generate_password_hash, check_password_hash


@login.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    password_hash = db.Column(db.String(128))

    uploads = db.relationship('Upload', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @staticmethod
    def get_by_username(username):
        return User.query.filter(func.lower(User.username) == func.lower(username)).first()


class Upload(db.Model):
    __tablename__ = 'uploads'

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)

    @staticmethod
    def query_by_current_user():
        return Upload.query.filter(Upload.user_id == current_user.id)

