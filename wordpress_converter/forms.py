from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField, TextField, \
                        PasswordField, BooleanField, SelectMultipleField, \
                        FormField, FieldList
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
    
class AddCategoryForm(Form):
    """ Define form for adding a category. """
    add_category = TextField(label="Add a Category", description="Please enter a name for your category.", validators=[DataRequired()])
    add_button = SubmitField(label="Add")
    
class AddTagForm(Form):
    """ Define form for adding a category. """
    add_tag = TextField(label="Add a Tag", description="Please enter a name for your tag.", validators=[DataRequired()])
    add_button = SubmitField(label="Add")
    
class CategoryForm(Form):
    """ Form portion for a category - can be repeated. """
    cat_edit_box = TextField()
    
class EditCategoriesForm(Form):
    """ Form for edit/merge/delete categories. """
    #categories = FieldList(FormField(CategoryForm))
    categories = FieldList(TextField())

class MergeDeleteCategoryForm(Form):
    """ Form to merge/delete categories. """
    categories = SelectMultipleField()
    
    merge_button = SubmitField(label="Merge")
    delete_button = SubmitField(label="Delete")
    cancel_button = SubmitField(label='Cancel')