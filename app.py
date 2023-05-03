"""Flask application that allows users to write notes for themselves and store them."""

import os

from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError

from models import connect_db, db, User, Note
from forms import RegisterForm, LoginForm, CSRFProtectForm, AddNoteForm, EditNoteForm

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///notes")
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"

connect_db(app)
db.create_all()

app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False
toolbar = DebugToolbarExtension(app)

# Root route
@app.get('/')
def homepage():
    
    form = CSRFProtectForm()

    return render_template("index.html", form=form)


# ////////////////////////////////////////////////////////////////////////////////////////////////////////////////
# Routes related to user login/logout/registration


@app.route('/register', methods=['GET', 'POST'])
def register():
    """Register user: produce form & handle form submission."""

    form = RegisterForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data

        user = User.register(username,
                             password,
                             email,
                             first_name,
                             last_name)

        # Attempt to add the user to the database and catch any IntegrityErrors
        try:
            db.session.add(user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash("Username or email already exists. Please choose a different one.")
            return render_template("register.html", form=form)

        session['username'] = user.username

        # on successful login, redirect to user page
        return redirect(f"/users/{user.username}")

    else:
        flash('All fields are required')
        return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Produce login form or handle login."""

    form = LoginForm()

    if form.validate_on_submit():
       username = form.username.data
       password = form.password.data

       # authenticate will return a user or False
       user = User.authenticate(username, password)

       if user:
            session["username"] = user.username  # keep logged in
            return redirect(f"/users/{username}")

       else:
            form.username.errors = ["Bad name/password"]

    return render_template("login.html", form=form)


@app.post("/logout")
def logout():
    """Logs user out and redirects to homepage."""

    form = CSRFProtectForm()

    if form.validate_on_submit():
        # Remove "username" if present, but no errors if it wasn't
        session.pop("username", None)

    return redirect("/")


# /////////////////////////////////////////////////////////////////////////////////////////////////////////////////
#  Routes related to User


@app.get('/users/<username>')
def show_user(username):
    """Show user page displaying info about the user and their notes if user is logged in."""

    if 'username' not in session or session['username'] != username:
        return redirect('/login')

    form = CSRFProtectForm()

    user = User.query.get_or_404(username)

    return render_template('user.html', user=user, form=form)

@app.post('/users/<username>/delete')
def remove_user(username):
    """ Remove user from db, redirect to login"""

    if 'username' not in session or session['username'] != username:
        return redirect('/login')

    form = CSRFProtectForm()

    #  delete the user and all of their notes, log them out
    if form.validate_on_submit():
        user = User.query.get_or_404(username)
        Note.query.filter_by(owner_username = username).delete()
        db.session.delete(user)
        db.session.commit()
        session.pop('username')

        return redirect('/')


# ////////////////////////////////////////////////////////////////////////////////////////
# Routes related to Notes

@app.route('/users/<username>/notes/add', methods=['GET', 'POST'])
def add_note(username):
    """Show form to add new note"""

    if 'username' not in session or session['username'] != username:
        return redirect('/login')

    form = AddNoteForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data

        note = Note(
            title=title,
            content=content,
            owner_username=username,
        )

        db.session.add(note)
        db.session.commit()

        return redirect(f"/users/{username}")

    else:
        # handle invalid submission (not logged in)
        return render_template("notes/new.html", form=form)

@app.route('/notes/<int:note_id>/update', methods=['GET', 'POST'])
def edit_note(note_id):
    """Show form to edit existing note"""

    note = Note.query.get_or_404(note_id)

    if 'username' not in session or session['username'] != note.owner_username:
        return redirect('/login')

    form = EditNoteForm(obj=note)

    if form.validate_on_submit():
        note.title = form.title.data
        note.content = form.content.data

        db.session.commit()

        return redirect(f'/users/{note.owner_username}')

    # handle invalid submission (not logged in)
    return render_template("notes/edit.html", form=form, note=note)

@app.post("/notes/<int:note_id>/delete")
def delete_note(note_id):
    """Delete note."""

    note = Note.query.get_or_404(note_id)

    if 'username' not in session or note.owner_username != session['username']:
        return redirect('/login')

    form = CSRFProtectForm()

    if form.validate_on_submit():

        db.session.delete(note)
        db.session.commit()

        return redirect(f"/users/{note.owner_username}")

    else:
        # handle invalid submission (not logged in)
        flash('You must be logged in!')
        return redirect('/register')
















