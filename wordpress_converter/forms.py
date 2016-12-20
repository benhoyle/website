from wtforms import Form, StringField, TextAreaField, SubmitField

class PostForm(Form):
    """ Form for adding and editing a post. """
    display_title = StringField(label="Post Title")
    
    content = TextAreaField(label="Post Text")
    
    enter_button = SubmitField(label="Save")