from flask_wtf import Form
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class PostForm(Form):
    """ Form for adding and editing a post. """
    display_title = StringField(label="Post Title", description="Please enter a title.", validators=[DataRequired()])
    
    content = TextAreaField(label="Post Text", description="Type post content here", validators=[DataRequired()])
    
    enter_button = SubmitField(label="Save")