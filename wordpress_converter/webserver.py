#from .core import WPParser

import os

import datetime

# Import flask and template operators
from flask import Flask, render_template, request, redirect, url_for

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

from wordpress_converter import app, db

# Import models
from wordpress_converter.models import Post, Tag, Category, Author

# Import forms
from wordpress_converter.forms import PostForm 

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
    
@app.errorhandler(500)
def internal_error(exception):
    app.logger.error(exception)
    return render_template('500.html'), 500
    
@app.route('/posts', methods=['GET'])
@app.route('/', methods=['GET'])
def show_posts():
    posts = Post.query.order_by(Post.date_published.desc()).all()
    return render_template('postwall.html', posts=posts)
    
@app.route('/posts/<nicename>', methods=['GET'])
def post(nicename):
    post = Post.query.filter(Post.nicename == nicename).first()
    return render_template('post.html', post=post)
    
@app.route('/posts/<nicename>/edit', methods=['GET', 'POST'])
def edit_post(nicename):
    post = Post.query.filter(Post.nicename == nicename).first()
    if not post:
        return redirect(url_for('show_posts'))
    form = PostForm(request.form, post)
    if post and form.validate_on_submit():
        form.populate_obj(post)
        post.make_nicename()
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('post', nicename=post.nicename))
    return render_template('add_edit.html', form=form)
    
@app.route('/posts/add', methods=['GET', 'POST'])
def add_post():
    form = PostForm()
    if form.validate_on_submit():
        post = Post()
        post.display_title = form.display_title.data 
        post.content = form.content.data
        post.date_published = datetime.datetime.now()
        date_published_year = post.date_published.year
        date_published_month = post.date_published.month
        post.status = "publish"
        post.excerpt = ""
        post.make_nicename()
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('post', nicename=post.nicename))
    return render_template('add_edit.html', form=form)

@app.route('/categories', methods=['GET'])
def show_categories():
    categories = Category.query.order_by(Category.display_name.asc()).all()
    return render_template('categories.html', categories=categories)

@app.route('/categories/<category_nicename>', methods=['GET'])
def category_postwall(category_nicename):
    category = Category.query.filter(Category.nicename == category_nicename).first()
    posts = category.posts.order_by(Post.date_published.desc()).all()
    return render_template('postwall.html', posts=posts, category=category)
    
@app.route('/tags', methods=['GET'])
def show_tags():
    tags = Tag.query.order_by(Tag.display_name.asc()).all()
    return render_template('tags.html', tags=tags)

@app.route('/tags/<tag_nicename>', methods=['GET'])
def tag_postwall(tag_nicename):
    tag = Tag.query.filter(Tag.nicename == tag_nicename).first()
    posts = tag.posts.order_by(Post.date_published.desc()).all()
    return render_template('postwall.html', posts=posts, tag=tag)

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
    # Do we want to get rid of os import for security?
    app.run(host=os.environ.get("HOST"))