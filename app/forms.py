from flask_wtf import FlaskForm
from app.models import User
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import Length, Email, EqualTo, DataRequired, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired

class SignUpForm(FlaskForm):
    def validate_username(self, username_to_check):
        username_check = User.query.filter_by(username=username_to_check.data).first()
        if username_check:
            raise ValidationError("This username is already used!")
    def validate_email_address(self, email_to_check):
        email_check = User.query.filter_by(email=email_to_check.data).first()
        if email_check:
            raise ValidationError("This Email is already registered!")

    firstName = StringField(label="FIRST NAME", validators=[ Length(min=2, max=12) ,DataRequired()])
    lastName = StringField(label="LAST NAME", validators=[Length(min=1, max=8), DataRequired()])
    username = StringField(label="USERNAME", validators=[Length(min=3, max=20) , DataRequired()])
    email_address = StringField(label="EMAIL ADDRESS", validators=[Email() ,DataRequired()])
    password = PasswordField(label="PASSWORD", validators=[Length(min=8), DataRequired()])
    confirm_password = PasswordField(label="CONFIRM PASSWORD", validators=[EqualTo('password'), DataRequired()])
    submit = SubmitField(label="CREATE ACCOUNT")


class LogInForm(FlaskForm):
    username = StringField(label="USERNAME", validators=[DataRequired()])
    email_address = StringField(label="EMAIL", validators=[DataRequired()])
    password = PasswordField(label="PASSWORD", validators=[DataRequired()])
    submit = SubmitField(label="LOG IN")

class NoteForm(FlaskForm):
    title = StringField()
    data = TextAreaField()
    add_note = SubmitField(label="Add Note")
class DeleteNoteForm(FlaskForm):
    delete = SubmitField(label="Delete")

class ChangeInfoForm(FlaskForm):
    change_username = StringField(label="Username")
    change_password = PasswordField()
    change_pic = FileField(label="Update Profile Picture:", validators=[FileAllowed(['png', 'jpg']), FileRequired()])
    submit = SubmitField(label="Save changes")
class ChangePassForm(FlaskForm):
    old_pass = PasswordField(label="Old Password", validators=[DataRequired()])
    new_pass = PasswordField(label="New Password", validators=[Length(min=8), DataRequired()])
    confirm_new_pass = PasswordField(label="Confirm New Password", validators=[EqualTo('new_pass'), DataRequired()])
