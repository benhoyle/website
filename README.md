# Wordpress Export File Converter
A tool to convert Wordpress.com export XML files to static HTML files or a Flask Website.

## Install Requirements
Navigate to the project directory with ```requirements.txt```. 
Activate your virtual environment (e.g. activate / source activate project).
Then ``` pip install -r requirements.txt```

Then install the present files as a local package (I'll upload to PyPi when
more developed). In the project directory with ```setup.py``` run:
```pip install -e```

## Static HTML Usage
```
from wordpress_converter import WPParser
wpc = WPParser("/path/to/file/blog.xml", "/path/to/export_folder/")
# Get attachments, e.g. image files and save to "files" folder
wpc.get_files()
# Convert posts to HTML and save to "posts" folder
wpc.posts_to_html()
```

## Flask Website Usage

First set up environment variables. For example, in a shell script (that is loaded
on environment activation):
```
#!/bin/sh
export HOST='[IP address of computer]'
export PORT='80'
export CSRF_SESSION_KEY='[your_secret]'
export SECRET_KEY='[another_secret]'
export DATABASE_URL='sqlite:////path/to/your/desiredwebsite.db'
export IMAGES_URL='path/to/your/desired/static/imagesdirectory/'
export RELATIVE_IMAGES_URL='/static/images/'
export APP_SETTINGS='config.DevelopmentConfig'
```

In the Python interpretor:
```
from wordpress_converter import WPFlaskParser
wpc = WPFlaskParser("/path/to/file/blog.xml")
# Perform conversion
wpc.save_all()
```

# Setup Passwords for Existing Authors

The import process should add the authors from the XML file.

To set author/user passwords (to allow logins and add/edit/delete functions), 
run from the command line:
```python -m wordpress_converter.set_password```
This will then prompt for the login name of an author and give you the chance
to enter a password.

# Activate Web Server (Development Environment)

Use this for viewing / testing not for production!

At the command line:
```python -m wordpress_convertor.webserver```

Navigate your browser to http://localhost/ or http://[your_ip]:[your_port].