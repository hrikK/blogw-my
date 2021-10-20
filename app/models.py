from app import db, bcrypt, login_manager
from flask_login import UserMixin, current_user
from sqlalchemy.sql import func


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    firstName = db.Column(db.String(length=12), nullable=False)
    lastName = db.Column(db.String(length=8), nullable=False)
    username = db.Column(db.String(length=20), nullable=False, unique=True)
    email = db.Column(db.String(), nullable=False, unique=True)
    password_hash = db.Column(db.String(), nullable=False)
    profile_pic = db.Column(db.String(), nullable=False, default="default.jpg")
    notes = db.relationship('Notes', lazy=True, backref="note_owner")


    @property
    def password(self):
        return self.password

    @password.setter
    def password(self, given_password):
        self.password_hash = bcrypt.generate_password_hash(given_password).decode('utf-8')

    def password_hash_check(self, given_password):
        return bcrypt.check_password_hash(self.password_hash, given_password)

    def create_note(self, note_title, note_data):
        note_info = Notes(title=note_title, data=note_data, user_id=current_user.id)
        db.session.add(note_info)
        db.session.commit()
        
    def delete_note(self, note_to_delete):
        db.session.delete(note_to_delete)
        db.session.commit()

    def check_username(self, username_to_check):
        given_username = User.query.filter_by(username=username_to_check).first()
        
        if not given_username:
            return True
        else: 
            return False
    def username_change(self, given_username):
        current_user.username = given_username
        db.session.add(current_user)
        db.session.commit()
    def password_change(self, given_password):
        current_user.password = given_password.new_pass.data
        db.session.commit()



class Notes(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String(length=100), nullable=True)
    data = db.Column(db.String(length=10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'))


