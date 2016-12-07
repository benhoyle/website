# Wordpress Export File Converter
A tool to convert Wordpress.com export XML files to static HTML files.

## Usage
'''
from wordpress_converter import WPParser
wpc = WPParser("/path/to/file/blog.xml", "/path/to/export_folder/")
# Get attachments, e.g. image files and save to "files" folder
wpc.get_files()
# Convert posts to HTML and save to "posts" folder
wpc.posts_to_html()

