from bs4 import BeautifulSoup
import os
import requests
import html

from wordpress_converter import models as m

def attachment_tag_match(tag):
    """ Returns true if tag has a child with post_type = attachment. """
    if hasattr(tag, "post_type"):
        if hasattr(tag.post_type, "text"):
            return tag.post_type.text == "attachment"
    
def post_tag_match(tag):
    """ Returns true if tag has a child with post_type = attachment. """
    if hasattr(tag, "post_type"):
        if hasattr(tag.post_type, "text"):
            return tag.post_type.text == "post"
    
def page_tag_match(tag):
    """ Returns true if tag has a child with post_type = attachment. """
    if hasattr(tag, "post_type"):
        if hasattr(tag.post_type, "text"):
            return tag.post_type.text == "page"

def get_dir(foldername, path):
    """ Get directory relative to current file - if it doesn't exist create it. """
    file_dir = os.path.join(path, foldername)
    if not os.path.isdir(file_dir):
        os.mkdir(os.path.join(path, foldername))
    return file_dir

class WPParser:
    """ Class wrapper for parsing functions."""
    
    def __init__(self, path_to_file, output_path):
        """ Initialise parser with the filename of a Wordpress export XML file. 
            Save folder structure in 'output_path' """
        with open(path_to_file, 'r') as f:
            filedata = f.read()
        self.soup = BeautifulSoup(filedata, "xml")
        
        # Set folder path from filename
        parent_foldername = os.path.split(path_to_file)[1].split('.')[0]
        self.path = get_dir(parent_foldername, output_path)
        
    def get_files(self, foldername="files"):
        """ Download images from blog and store in a static "images" folder. """
        # Images are stored as "items" (as are posts) with accompanying metadata
        
        # Make directory if it doesn't exist
        file_dir = get_dir(foldername, self.path)
        
        # Find all 'item' tags where <wp:post_type> = attachment
        attachments = self.soup.find_all(attachment_tag_match)
        
        for attachment in attachments: 
            # Check if file exists - only download if it doesn't
            filename = os.path.join(file_dir, os.path.split(attachment.attachment_url.text)[1])
            if not os.path.exists(filename):
                try:
                    # Download file
                    img_data = requests.get(attachment.attachment_url.text).content
                    # Save file
                    with open(filename, 'wb') as handler:
                        handler.write(img_data)
                except:
                    raise
    
    def __to_html(self, foldername, match_function):
        """ General function for extracting post and page data."""
        # Make directory if it doesn't exist
        file_dir = get_dir(foldername, self.path)
        
        # Find all 'item' tags where 'match_function' matches
        items = self.soup.find_all(match_function)
        
        for item in items:
            # Set filename format as post_name
            filename = os.path.join(file_dir, "".join([item.post_date.text, " ", item.post_name.text, ".html"]))
            if not os.path.exists(filename):
                item_data = html.unescape(item.encoded.text)
            
                with open(filename, 'w') as handler:
                    handler.write(item_data)
    
    def posts_to_html(self, foldername="posts"):
        """ Extract posts and save as HTML files in folder with foldername. """
        self.__to_html(foldername, post_tag_match)
    
    def pages_to_html(self, foldername="pages"):
        """ Extract posts and save as HTML files in folder with foldername. """
        self.__to_html(foldername, page_tag_match)
        
    def convert_file_links(self, foldername):
        """ Process HTML files in foldername and replace Wordpress URLs with 
        local urls to 'files' directory. """
        # to do
        pass
        
    def build_date_index(self, foldername):
        """ Build an HTML date index from files in foldername (e.g. "posts"). """
        # to do
        pass
        
class WPFlaskParser:
    """ Class wrapper for parsing functions to create DB for Flask."""
    
    def __init__(self, path_to_file):
        """ Initialise parser with the filename of a Wordpress export XML file. 
            Output file is set by environment variable DATABASE_URL.
            (As environment variable is used by Flask. """
        with open(path_to_file, 'r') as f:
            filedata = f.read()
        self.soup = BeautifulSoup(filedata, "xml")
    
    def save_tags(self):
        """ Save tags in the database."""
        xml_tags = self.soup.find_all("tag")
        for xml_tag in xml_tags:
            if not m.Tag.exists(xml_tag.tag_slug.text):
                new_db_tag = m.Tag(
                    nicename=xml_tag.tag_slug.text, 
                    display_name=html.unescape(xml_tag.tag_name.text)
                    )
                m.db.session.add(new_db_tag)
                m.db.session.commit()
        
    def save_categories(self):
        """ Save categories in the database. """
        xml_categories = self.soup.find_all("category")
        for xml_category in xml_categories:
            if not m.Category.exists(xml_category.category_nicename.text):
                new_db_category = m.Category(
                    nicename=xml_category.category_nicename.text, 
                    display_name=html.unescape(xml_category.cat_name.text)
                    )
                if xml_category.category_parent.text:
                    new_db_category = new_db_category.add_parent(xml_category.category_parent.text) 
                m.db.session.add(new_db_category)
                m.db.session.commit()
        
    def save_posts(self):
        """ Save posts in the database. """