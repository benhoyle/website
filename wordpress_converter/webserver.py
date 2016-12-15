#from .core import WPParser

import os

# Import flask and template operators
from flask import Flask, render_template

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

from wordpress_converter import app, db

# Import models
from wordpress_converter.models import Post, Tag, Category, Author

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
    
@app.errorhandler(500)
def internal_error(exception):
    app.logger.error(exception)
    return render_template('500.html'), 500
    
@app.route('/postwall', methods=['GET'])
def postwall():
    posts = Post.query.order_by(Post.date_published.desc()).all()
    return render_template('postwall.html', posts=posts)
    
@app.route('/post/<nicename>', methods=['GET'])
def post(nicename):
    post = Post.query.filter(Post.nicename == nicename).first()
    return render_template('post.html', post=post)

@app.route('/categories', methods=['GET'])
def show_categories():
    #Just list all categories
    categories = Category.query.order_by(Category.display_name.asc()).all()
    return render_template('categories.html', categories=categories)

@app.route('/postwall/category/<category_nicename>', methods=['GET'])
def category_postwall(category_nicename):
    category = Category.query.filter(Category.nicename == category_nicename).first()
    posts = category.posts.order_by(Post.date_published.desc()).all()
    return render_template('postwall.html', posts=posts, category=category)

# Configure lines
import logging
from logging.handlers import RotatingFileHandler

if app.debug is not True:
    file_handler = RotatingFileHandler('attass_error.log', maxBytes=1024 * 1024 * 100, backupCount=20)
    file_handler.setLevel(logging.INFO)
    app.logger.setLevel(logging.INFO)
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    app.logger.addHandler(file_handler)

# Run app for apache deployment    
if __name__ == "__main__":
    app.run()