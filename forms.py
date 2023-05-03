from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField
from wtforms.validators import InputRequired, Email, Length

class RegisterForm(FlaskForm):
    """Form for registering a user."""

    username = StringField(
        "Username",
        validators=[InputRequired(), Length(min= 1,
                                            max= 20,
                                            message='Username must be less than 20 characters')]
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired(), Length(min= 1,
                                            max= 100,
                                            message='Password must be less than 100 characters')]
    )
    # TODO: add email validator??
    email = EmailField(
        "Email",
        validators=[InputRequired(), Length(min= 1,
                                            max= 50,
                                            message='Email must be less than 50 characters')]
    )

    first_name = StringField(
        "First Name",
        validators=[InputRequired(), Length(min= 1,
                                            max= 30,
                                            message='First name must be less than 30 characters')]
    )

    last_name = StringField(
        "Last Name",
        validators=[InputRequired(), Length(min= 1,
                                            max= 30,
                                            message='Last name must be less than 30 characters')]
    )




class LoginForm(FlaskForm):
    """Form for loggin in existing user."""

    username = StringField(
        "Username",
        validators=[InputRequired()]
    )

    password = PasswordField(
        "Password",
        validators=[InputRequired()]
    )

class CSRFProtectForm(FlaskForm):
    """Form just for CSRF Protection"""


class AddNoteForm(FlaskForm):
    """ Form to add a new note"""

    title = StringField(
        "Title",
        validators=[InputRequired(), Length(min= 1,
                                            max= 100,
                                            message='Title must be less than 100 characters')]
        )

    content = TextAreaField(
        'Content',
        validators=[InputRequired()]
        )

class EditNoteForm(AddNoteForm):
    """Form for editing notes."""
