#from .core import WPParser

import os

import datetime

# Import flask and template operators
from flask import Flask, render_template, request, redirect, url_for, \
                    g, session, flash

# Import SQLAlchemy
from flask_sqlalchemy import SQLAlchemy

# Import Login Manager
from flask_login import LoginManager, login_user, logout_user, current_user, login_required

from wordpress_converter import app, db

# Import models
from wordpress_converter.models import Post, Tag, Category, Author

# Import forms
from wordpress_converter.forms import PostForm, DeleteConfirm, LoginForm

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
    
@app.errorhandler(500)
def internal_error(exception):
    app.logger.error(exception)
    return render_template('500.html'), 500

# Start login manager
lm = LoginManager()
lm.init_app(app)
lm.login_view = 'login'

# Login manager user loader
@lm.user_loader
def load_user(id):
    return Author.query.get(int(id))
    
@app.before_request
def before_request():
    g.user = current_user
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    # If user is already logged in go straight to homepage
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('show_posts'))
    # Generate login form
    form = LoginForm(request.form)

    # Verify the sign in form
    if form.validate_on_submit():
        session['remember_me'] = form.remember_me.data
        
        user = Author.query.filter(Author.login==form.login.data).first()
        if user and user.check_password(form.password.data):
            session['user_id'] = user.id
            remember_me = False
            if 'remember_me' in session:
                remember_me = session['remember_me']
                session.pop('remember_me', None)
            login_user(user, remember = remember_me)
            flash('Welcome %s' % user.display_name)
            return redirect(url_for('show_posts'))
        flash('Wrong email or password', 'error-message')

    return render_template("login.html", form=form)
    
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('show_posts'))

@app.route('/posts', methods=['GET'])
@app.route('/', methods=['GET'])
def show_posts():
    posts = Post.query.filter(Post.status=="publish").order_by(Post.date_published.desc()).all()
    return render_template('postwall.html', posts=posts)

@app.route('/posts/drafts', methods=['GET'])
def show_drafts():
    posts = Post.query.filter(Post.status=="draft").order_by(Post.date_updated.desc()).all()
    return render_template('postwall.html', posts=posts)

@app.route('/posts/<nicename>', methods=['GET'])
def post(nicename):
    if g.user is not None and g.user.is_authenticated:
        # Show drafts as well as published posts
        post = Post.query.filter(Post.nicename == nicename).first()
    else:
        # Only show published posts
        post = Post.query.filter(Post.status=="publish").filter(Post.nicename == nicename).first()
    if not post:
        return redirect(url_for('show_posts'))
    return render_template('post.html', post=post)
    
@app.route('/posts/<nicename>/edit', methods=['GET', 'POST'])
@login_required
def edit_post(nicename):
    post = Post.query.filter(Post.nicename == nicename).first()
    if not post:
        return redirect(url_for('show_posts'))
    form = PostForm(request.form, post)
    form.categories.choices = Category.get_category_names()
    form.tags.choices = Tag.get_tag_names()
    if request.method == "GET":
        # Preselect tags and categories
        form.categories.process_data(post.get_category_nicenames())
        form.tags.process_data(post.get_tag_nicenames())
    if form.validate_on_submit():
        if form.cancel.data:
            return redirect(url_for('post', nicename=post.nicename))
        if form.save_as_draft_button.data:
            post.status = "draft"
        if form.publish_button.data:
            post.status = "publish"
            if not post.date_published:
                post.date_published = datetime.datetime.now()
                date_published_year = post.date_published.year
                date_published_month = post.date_published.month
        post.date_updated = datetime.datetime.now()
        post.display_title = form.display_title.data
        post.content = form.content.data
        post.make_nicename()
        for category in form.categories.data:
            post.categorise_by_nicename(category)
        for tag in form.tags.data:
            post.tag_by_nicename(tag)
        db.session.add(post)
        db.session.commit()
        return redirect(url_for('post', nicename=post.nicename))
    return render_template('add_edit.html', form=form)
    
@app.route('/posts/add', methods=['GET', 'POST'])
@login_required
def add_post():
    form = PostForm()
    form.categories.choices = Category.get_category_names()
    form.tags.choices = Tag.get_tag_names()
    if form.validate_on_submit():
        if form.cancel.data:
            return redirect(url_for('post', nicename=post.nicename))
        
        post = Post()
        post.display_title = form.display_title.data 
        post.content = form.content.data
        post.date_updated = datetime.datetime.now()
        post.make_nicename()
        if form.save_as_draft_button.data:
            post.status = "draft"
        if form.publish_button.data:
            post.status = "publish"
            post.date_published = datetime.datetime.now()
            date_published_year = post.date_published.year
            date_published_month = post.date_published.month
        post.excerpt = ""
        
        db.session.add(post)
        for category in form.categories.data:
            post.categorise_by_nicename(category)
        for tag in form.tags.data:
            post.tag_by_nicename(tag)
        post.add_author_by_login(g.user.login)
        
        
        db.session.commit()
        return redirect(url_for('post', nicename=post.nicename))
    return render_template('add_edit.html', form=form)

@app.route('/posts/<nicename>/delete', methods=['GET', 'POST'])
@login_required
def delete_post(nicename):
    post = Post.query.filter(Post.nicename == nicename).first()
    if not post:
        return redirect(url_for('show_posts'))
    form = DeleteConfirm(request.form)
    if form.validate_on_submit():
        if form.confirm_delete.data:
            db.session.delete(post)
            db.session.commit()
            return redirect(url_for('show_posts'))
        if form.cancel.data:
            return redirect(url_for('post', nicename=post.nicename))
    return render_template('confirm_delete.html', post=post, form=form)

@app.route('/categories', methods=['GET'])
def show_categories():
    categories = Category.query.order_by(Category.display_name.asc()).all()
    return render_template('categories.html', categories=categories)

@app.route('/categories/<category_nicename>', methods=['GET'])
def category_postwall(category_nicename):
    category = Category.query.filter(Category.nicename == category_nicename).first()
    posts = category.posts.filter(Post.status=="publish").order_by(Post.date_published.desc()).all()
    return render_template('postwall.html', posts=posts, category=category)
    
@app.route('/tags', methods=['GET'])
def show_tags():
    tags = Tag.query.order_by(Tag.display_name.asc()).all()
    return render_template('tags.html', tags=tags)

@app.route('/tags/<tag_nicename>', methods=['GET'])
def tag_postwall(tag_nicename):
    tag = Tag.query.filter(Tag.nicename == tag_nicename).first()
    posts = tag.posts.filter(Post.status=="publish").order_by(Post.date_published.desc()).all()
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