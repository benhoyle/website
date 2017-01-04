from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField, TextField, \
                        PasswordField, BooleanField, SelectMultipleField
from wtforms.validators import DataRequired, Required, EqualTo, Email

class PostForm(Form):
    """ Form for adding and editing a post. """
    display_title = StringField(label="Post Title", description="Please enter a title.", validators=[DataRequired()])
    categories = SelectMultipleField("Categories")
    tags = SelectMultipleField("Tags")
    content = TextAreaField(label="Post Text", description="Type post content here", validators=[DataRequired()])
    
    publish_button = SubmitField(label="Publish")
    save_as_draft_button = SubmitField(label="Save As Draft")
    cancel = SubmitField(label='Cancel')
    
class DeleteConfirm(Form):
    """ Short form to work as a confirm delete modal button. """
    confirm_delete = SubmitField(label='Confirm Delete')
    cancel = SubmitField(label='Cancel')

class LoginForm(Form):
    """ Define the login form. """
    login = TextField('User login', [Required(message='Forgot your login name?')])
    password = PasswordField('Password', [Required(message='Must provide a password. ;-)')])
    remember_me = BooleanField('remember_me', default=False)

class SignupForm(Form):
    """ Define the form for registering a user."""
    login  = TextField('Login name', [Required()])
    firstname = TextField('First Name', [Required()])
    surname   = TextField('Surname', [Required()])
    email     = TextField('Email Address', [Email(), Required()])
    password  = PasswordField('New Password', [Required(), EqualTo('confirm', message='Passwords must match')])
    confirm   = PasswordField('Repeat Password')