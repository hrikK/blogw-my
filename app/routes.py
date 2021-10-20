import secrets, os
from PIL import Image
from flask import render_template, url_for, redirect, flash, request
from flask_login import login_user, logout_user, current_user, login_required
from app import app,db
from app.forms import SignUpForm, LogInForm, NoteForm, DeleteNoteForm, ChangeInfoForm, ChangePassForm
from app.models import User, Notes

@app.route("/")
def home_page():
    return render_template("index.html")

@app.route("/notes", methods=["GET", "POST"])
@login_required
def notes_page():
    note_form = NoteForm()
    delete_note = DeleteNoteForm()

    if request.method == "POST":
        if "add_note" in request.form:
            note_title = request.form.get("title")
            note_data = request.form.get("data")
            if note_data and note_title:
                note_info = Notes(title=note_title, data=note_data, user_id=current_user.id)
                db.session.add(note_info)
                db.session.commit()
                flash("Added a new note!", category="success")
            else:
                if not note_title:
                    flash("Please give a title to your note!", category="danger")
                else:
                    flash("Your note is empty!", category="danger")

        if "delete_note" in request.form:
            note_id = request.form.get("delete_note")
            note_to_delete = Notes.query.filter_by(id=note_id).first()
            if note_to_delete:
                current_user.delete_note(note_to_delete)
                flash("Your note was deleted!", category="success")
            else:
                flash(f"Couldn't delete note!{note_to_delete}", category="danger")
        
        return redirect(url_for("notes_page"))
    if request.method == "GET":
        notes=Notes.query.filter_by(user_id=current_user.id)
        return render_template("notes.html", notes=notes, note_form=note_form, delete_note=delete_note)



@app.route("/sign-up", methods=["GET", "POST"])
def sign_up_page():
    form = SignUpForm()
    if form.validate_on_submit():
        user_info = User(firstName=form.firstName.data,
                         lastName=form.lastName.data,
                         email=form.email_address.data,
                         username=form.username.data,
                         password=form.password.data)
        db.session.add(user_info)
        db.session.commit()
        flash(f"Successfully created a new account for {form.username.data}!", category="success")
        return redirect(url_for("log_in_page"))
    if form.errors != {}:
        for err_msg in form.errors.values():
            if err_msg == ['This username is already used!']:
                flash(f"Username: {form.username.data} is already used!", category="danger")
            elif err_msg == ['Field must be between 3 and 20 characters long.']:
                flash("Username must be between 3 and 20 characters long!", category="danger")
            elif err_msg == ['Invalid email address.']:
                flash("Email Address is not valid!", category="danger")
            elif err_msg == ['This Email is already registered!']:
                flash("This Email is already registered!", category="danger")
            elif err_msg == ['Field must be equal to password.']:
                flash(f"Passwords don't match!", category="danger")
            elif err_msg == ['Field must be at least 8 characters long.']:
                flash("Password must be 8 characters long!", category="danger")
            elif err_msg == ['Field must be between 2 and 12 characters long.']:
                flash("First Name must be between 1 and 8 characters long!", category="danger")
            elif err_msg == ['Field must be between 2 and 12 characters long.']:
                flash("Last Name must be between 2 and 12 characters long!", category="danger")
            else:
                flash(f"{err_msg}", category="danger")
    return render_template("sign_up.html", form=form)


@app.route("/log-in", methods=["GET", "POST"])
def log_in_page():
    form = LogInForm()
    if form.validate_on_submit():
        attemted_user = User.query.filter_by(username=form.username.data, email=form.email_address.data).first()
        if attemted_user != None and attemted_user.password_hash_check(form.password.data):
                login_user(attemted_user)
                flash(f"Successfully logged in as: {attemted_user.username}", category="success")
                return redirect(url_for("notes_page"))
        else:
            if not User.query.filter_by(email=form.email_address.data).first():
                flash("This Email is not registered!", category="danger")
            elif not User.query.filter_by(username=form.username.data).first():
                flash("Username and Email doesn't match!", category="danger")
            elif not attemted_user:
                flash("Username and Email didn't match!", category="danger")
            else:
                flash("Password doesn't match!", category="danger")
    return render_template("log_in.html", form=form)

def save_picture(picture_info):
    random_hex = secrets.token_hex(8)
    _ , p_ext = os.path.splitext(picture_info.filename)
    picture_name = random_hex + p_ext
    p_path = os.path.join(app.root_path, 'static/uploads', picture_name)

    output_size = (220, 210)
    i = Image.open(picture_info)
    i.thumbnail(output_size)
    i.save(p_path)
    
    return picture_name


@app.route("/account-info", methods=["GET", "POST"])
@login_required
def account_page():
    display_image = url_for('static', filename=f"uploads/{current_user.profile_pic}")
    change_info = ChangeInfoForm()
    change_pass = ChangePassForm()

    if request.method == "POST":
        if "update_pic" in request.form:
            if change_info.validate_on_submit():
                if change_info.change_pic.data:
                    picture_file = save_picture(change_info.change_pic.data)
                    current_user.profile_pic = picture_file
                    db.session.commit()
                    flash("Changed Profile Picture!", category="success")
            else:
                flash("Only png & jpg images are allowed!", category="danger")
    # Changing Username
        if "submit_username" in request.form:
            given_username = request.form.get("change_username")
            if given_username:
                if current_user.check_username(given_username):
                    current_user.username_change(given_username)
                    flash("Successfully changed username!", category="success")
                else:
                    flash(f"Username already exits!{given_username}", category="danger")
            else:
                flash("Input field is empty!", category="danger")
        # Changing Password
        if "pass_confirm" in request.form:
            old_pass = request.form.get("old_pass")
            new_pass = request.form.get("new_pass")
            if current_user.password_hash_check(old_pass):
                if old_pass != new_pass:
                    if change_pass.validate_on_submit():
                        current_user.password_change(change_pass)
                        logout_user()
                        flash("Succefully changed password. Login again now!", category="success")
                        return redirect(url_for("log_in_page"))
                    else:
                        for err_msg in change_pass.errors.values():
                            if err_msg == ['Field must be at least 8 characters long.']:
                                flash("Password must be 8 characters long!", category="danger")
                            else:
                                flash(f"New passwords don't match!", category="danger")
                            print(err_msg)
                else:
                    flash("Please use a new password!", category="danger")
            else:
                flash("Old password didn't match!", category="danger")
        return redirect(url_for('account_page'))
    if request.method == "GET":
        return render_template("account.html", change_info=change_info, change_pass=change_pass, display_image=display_image)


@app.route("/log-out")
def log_out_page():
    logout_user()
    flash(f"Logged out!", category="success")
    return redirect(url_for("home_page"))


