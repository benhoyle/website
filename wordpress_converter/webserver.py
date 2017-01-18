#from .core import WPParser

import os

import datetime

# Import flask and template operators
from flask import render_template, request, redirect, url_for, \
                    g, session, flash

import jinja2

# Import Login Manager
from flask_login import LoginManager, login_user, logout_user, current_user, login_required

from wordpress_converter import app, db

# Import models
from wordpress_converter.models import Post, Tag, Category, Author

# Import forms
from wordpress_converter.forms import PostForm, DeleteConfirm, LoginForm, \
                                        AddCategoryForm, EditCategoryForm, \
                                        MergeDeleteCategoryForm, MergeDeleteTagForm, \
                                        EditTagForm, AddTagForm

# Sample HTTP error handling
@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404
    
@app.errorhandler(500)
def internal_error(exception):
    app.logger.error(exception)
    return render_template('500.html'), 500

# Add custom jinja2 filter for rendering posts
@app.template_filter()
def contentfilter(content):
    """ Split into lines and format paragraphs """
    output_lines = []
    p_on = True
    for line in content.strip().splitlines():
        if len(line.strip()) > 0:
            if line[0] == "<" and line[-1] == ">":
                if "<pre>" in line:
                    p_on = False
                if "</pre>" in line:
                    p_on = True
                output_lines.append(line)
            else:
                if p_on:
                    output_lines.append("<p>" + line.strip() + "</p>")
                else:
                    output_lines.append(line)
    return "\n".join(output_lines)

app.jinja_env.filters['contentfilter'] = contentfilter


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
        # Need to add here removal of category
        for category in post.categories:
            if category.nicename not in form.categories.data:
                post.uncategorise(category)
        for category in form.categories.data:
            post.categorise_by_nicename(category)
        for tag in post.tags:
            if tag.nicename not in form.tags.data:
                post.untag(tag)
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
@app.cache.cached(timeout=300)
def show_tags():
    tags = Tag.query.order_by(Tag.display_name.asc()).all()
    return render_template('tags.html', tags=tags)

@app.route('/tags/<tag_nicename>', methods=['GET'])
def tag_postwall(tag_nicename):
    tag = Tag.query.filter(Tag.nicename == tag_nicename).first()
    posts = tag.posts.filter(Post.status=="publish").order_by(Post.date_published.desc()).all()
    return render_template('postwall.html', posts=posts, tag=tag)

@app.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_categories():
    categories = Category.query.order_by(Category.display_name.asc()).all()
    add_form = AddCategoryForm()
    if request.method == "POST":
        if add_form.validate_on_submit() and add_form.add_button.data:
            print(add_form.add_category.data)
            category=Category(display_name=add_form.add_category.data)
            category.make_nicename()
            if Category.exists(category.nicename):
                add_form.add_category.errors.append("Category already exists")
            else:
                db.session.add(category)
                db.session.commit()
                return redirect(url_for('add_categories'))
    return render_template('add_categories.html', categories=categories, add_form=add_form)

@app.route('/categories/edit', methods=['GET', 'POST'])
@login_required
def edit_categories():
    categories = Category.query.order_by(Category.display_name.asc()).all()
    edit_form = EditCategoryForm()
    edit_form.categories.choices = Category.get_category_names()
    if request.method == "POST":
        if edit_form.cancel_button.data:
            return redirect(url_for('show_categories'))
        if edit_form.validate_on_submit() and edit_form.edit_button.data:
            selected_category_nicename = edit_form.categories.data
            category = Category.get_by_nicename(selected_category_nicename)
            if category:
                category.display_name = edit_form.cat_edit_box.data
                category.make_nicename()
                db.session.add(category)
                db.session.commit()
                return redirect(url_for('show_categories'))
                    
    return render_template('edit_categories.html', edit_form=edit_form)

@app.route('/categories/merge_delete', methods=['GET', 'POST'])
@login_required
def merge_delete_categories():
    categories = Category.query.order_by(Category.display_name.asc()).all()
 
    merge_delete_form = MergeDeleteCategoryForm()
    merge_delete_form.categories.choices = Category.get_category_names()
    
    if request.method == "POST":
        
        if merge_delete_form.cancel_button.data:
            return redirect(url_for('show_categories'))
        
        if merge_delete_form.validate_on_submit() and merge_delete_form.delete_button.data:
            for category_name in merge_delete_form.categories.data:
                category = Category.get_by_nicename(category_name)
                if category:
                    flash("Deleted category: " + category.display_name)
                    for post in category.posts:
                        post.uncategorise(category)
                        db.session.add(post)
                        flash("Category removed from post: " + post.display_title)
                    db.session.delete(category)
                    db.session.commit()
            return redirect(url_for('show_categories'))
        
        if merge_delete_form.validate_on_submit() and merge_delete_form.merge_button.data:
            if len(merge_delete_form.categories.data) > 1:
                cats_to_merge = [Category.get_by_nicename(category_name) for category_name in merge_delete_form.categories.data]
                new_category_name = " ".join([c.display_name for c in cats_to_merge])
                flash("Merged category added: "+new_category_name)
                new_category=Category(display_name=new_category_name)
                new_category.make_nicename()
                if Category.exists(new_category.nicename):
                    merge_delete_form.categories.errors.append("Select more than one category to merge")
                else:
                    db.session.add(new_category)
                    db.session.commit()
                    for category in cats_to_merge:
                        for post in category.posts:
                            post.categorise(new_category)
                            db.session.add(post)
                            flash("Post categorised with merged category> " + post.display_title)
                    db.session.commit()
                    flash("Delete old categories if no longer needed")
                    return redirect(url_for('show_categories'))
            else:
                merge_delete_form.categories.errors.append("Select more than one category to merge")
                        
    return render_template('md_categories.html', merge_delete_form=merge_delete_form)

@app.route('/tags/add', methods=['GET', 'POST'])
@login_required
def add_tags():
    tags = Tag.query.order_by(Tag.display_name.asc()).all()
    add_form = AddTagForm()
    if request.method == "POST":
        if add_form.validate_on_submit() and add_form.add_button.data:
            print(add_form.add_tag.data)
            tag=Tag(display_name=add_form.add_tag.data)
            tag.make_nicename()
            if Tag.exists(tag.nicename):
                add_form.add_tag.errors.append("Tag already exists")
            else:
                db.session.add(tag)
                db.session.commit()
                return redirect(url_for('add_tags'))
    return render_template('add_tags.html', tags=tags, add_form=add_form)

@app.route('/tags/edit', methods=['GET', 'POST'])
@login_required
def edit_tags():
    tags = Tag.query.order_by(Tag.display_name.asc()).all()
    edit_form = EditTagForm()
    edit_form.tags.choices = Tag.get_tag_names()
    if request.method == "POST":
        if edit_form.cancel_button.data:
            return redirect(url_for('show_tags'))
        if edit_form.validate_on_submit() and edit_form.edit_button.data:
            selected_tag_nicename = edit_form.tags.data
            tag = Tag.get_by_nicename(selected_tag_nicename)
            if tag:
                tag.display_name = edit_form.tag_edit_box.data
                tag.make_nicename()
                db.session.add(tag)
                db.session.commit()
                return redirect(url_for('show_tags'))
                    
    return render_template('edit_tags.html', edit_form=edit_form)

@app.route('/tags/merge_delete', methods=['GET', 'POST'])
@login_required
def merge_delete_tags():
    tags = Tag.query.order_by(Tag.display_name.asc()).all()
 
    merge_delete_form = MergeDeleteTagForm()
    merge_delete_form.tags.choices = Tag.get_tag_names()
    
    if request.method == "POST":
        
        if merge_delete_form.cancel_button.data:
            return redirect(url_for('show_tags'))
        
        if merge_delete_form.validate_on_submit() and merge_delete_form.delete_button.data:
            for tag_name in merge_delete_form.tags.data:
                tag = Tag.get_by_nicename(tag_name)
                if tag:
                    flash("Deleted tag: " + tag.display_name)
                    for post in tag.posts:
                        post.untag(tag)
                        db.session.add(post)
                        flash("Tag removed from post: " + post.display_title)
                    db.session.delete(tag)
                    db.session.commit()
            return redirect(url_for('show_tags'))
        
        if merge_delete_form.validate_on_submit() and merge_delete_form.merge_button.data:
            if len(merge_delete_form.tags.data) > 1:
                tags_to_merge = [Tag.get_by_nicename(tag_name) for tag_name in merge_delete_form.tags.data]
                new_tag_name = " ".join([c.display_name for c in tags_to_merge])
                flash("Merged tag added: "+new_tag_name)
                new_tag=Tag(display_name=new_tag_name)
                new_tag.make_nicename()
                if Tag.exists(new_tag.nicename):
                    merge_delete_form.tags.errors.append("Select more than one tag to merge")
                else:
                    db.session.add(new_tag)
                    db.session.commit()
                    for tag in tags_to_merge:
                        for post in tag.posts:
                            post.tag(new_tag)
                            db.session.add(post)
                            flash("Post tagged with merged tag> " + post.display_title)
                    db.session.commit()
                    flash("Delete old tags if no longer needed")
                    return redirect(url_for('show_tags'))
            else:
                merge_delete_form.categories.errors.append("Select more than one tag to merge")
                        
    return render_template('md_tags.html', merge_delete_form=merge_delete_form)

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
    app.run(host=os.environ.get("HOST"), port=int(os.environ.get("PORT")))