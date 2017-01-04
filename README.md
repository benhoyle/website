# Wordpress Export File Converter
A tool to convert Wordpress.com export XML files to static HTML files.

## Usage
```
from wordpress_converter import WPParser
wpc = WPParser("/path/to/file/blog.xml", "/path/to/export_folder/")
# Get attachments, e.g. image files and save to "files" folder
wpc.get_files()
# Convert posts to HTML and save to "posts" folder
wpc.posts_to_html()
```


## Setup Passwords for Existing Authors

The import process should add the authors from the XML file.

To set author/user passwords (to allow logins and add/edit/delete functions), 
run from the command line:
```python -m wordpress_converter.set_password```
This will then prompt for the login name of an author and give you the chance
to enter a password.
