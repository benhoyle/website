# -*- coding: utf-8 -*-

from datetime import datetime

from wordpress_converter import db

import re

class Base(db.Model):
    """ Extensions to Base class. """

    __abstract__  = True

    id =  db.Column(db.Integer, primary_key=True)
    
    def as_dict(self):
        """ Return object as a dictionary. """
        temp_dict = {}
        temp_dict['object_type'] = self.__class__.__name__
        for c in self.__table__.columns:
            cur_attr = getattr(self, c.name)
            # If datetime generate string representation
            if isinstance(cur_attr, datetime):
                cur_attr = cur_attr.strftime('%d %B %Y')
            temp_dict[c.name] = cur_attr
        return temp_dict
    
    def populate(self, data):
        """ Populates matching attributes of class instance. 
        param dict data: dict where for each entry key, value equal attributename, attributevalue."""
        for key, value in data.items():
            if hasattr(self, key):
                # Convert string dates into datetimes
                if isinstance(getattr(self, key), datetime) or str(self.__table__.c[key].type) == 'DATE':
                    value = datetime.strptime(value, "%d %B %Y")
                setattr(self, key, value)
                

# Define post to tag association table
post_tag = db.Table('post_tag', 
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'))
    )
    
# Define post to category association table
post_category = db.Table('post_category', 
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'))
    )

# Define post to author association table
post_author = db.Table('post_author', 
    db.Column('post_id', db.Integer, db.ForeignKey('post.id')),
    db.Column('author_id', db.Integer, db.ForeignKey('author.id'))
    )

class Category(Base):
    """ Model for blog categories. """
    __tablename__ = "category"
    # Category name in lower case with spaces replaced by dashes
    nicename = db.Column(db.String(256))
    # Category name with spaces and capitals
    display_name = db.Column(db.String(256))
    
    # parent is id of another category - use custom method to return children
    # parent is referred to by nicename
    parent = db.Column(db.Integer, db.ForeignKey('category.id'))
    
    @staticmethod
    def exists(nicename):
        """ Check if a category with nicename already exists. """
        return Category.query.filter(Category.nicename == nicename).count() > 0
        
    def add_parent(self, parent_nicename):
        """ Adds parent category based on parent_nicename. """
        parent_category = Category.query.filter(Category.nicename == parent_nicename).first()
        if parent_category:
            self.parent = parent_category.id
        return self
        
    #@classmethod
    #def get_posts_by_category(cls, category_nicename):
        #""" Return posts having category."""
        #catergory_id = cls.query.filter(cls.nicename == category_nicename).first()
        #if category_id:
            #return db.session.query(post_category).join(Post, (Post.id == post_category.c.post_id)).filter(post_category.c.category_id == category_id).all()
    
class Tag(Base):
    """ Model for blog tags. """
    __tablename__ = "tag"
    # Tag name in lower case with spaces replaced by dashes
    nicename = db.Column(db.String(256))
    # Tag name with spaces and capitals
    display_name = db.Column(db.String(256))
    
    @staticmethod
    def exists(nicename):
        """ Check if a tag with nicename already exists. """
        return Tag.query.filter(Tag.nicename == nicename).count() > 0
    
class Author(Base):
    """ Model for blog authors. """
    __tablename__ = "author"
    login = db.Column(db.String(64))
    email = db.Column(db.String(256))
    display_name = db.Column(db.String(256))
    first_name = db.Column(db.String(128))
    last_name = db.Column(db.String(128))
    
    @staticmethod
    def exists(login):
        """ Check if a tag with nicename already exists. """
        return Author.query.filter(Author.login == login).count() > 0
    
class Post(Base):
    """ Model for blog post. """
    __tablename__ = "post"
    display_title = db.Column(db.String(256))
    # Post name in lower case with spaces replaced by dashes
    nicename = db.Column(db.String(256))
    content = db.Column(db.Text)
    # Short post summary for display 
    excerpt = db.Column(db.Text)
    # date post first published
    date_published = db.Column(db.DateTime)
    # Store year and month separately to allow for quick archive link generation
    date_published_year = db.Column(db.Integer)
    date_published_month = db.Column(db.Integer)
    # date post updated
    date_updated = db.Column(db.DateTime)
    # status - draft = not public, publish = published on Internet
    status = db.Column(db.String(25))
    
    authors = db.relationship('Author',
                        secondary=post_author,
                        backref=db.backref('posts', lazy='dynamic'),
                        lazy='dynamic')
                        
    
    tags = db.relationship('Tag',
                        secondary=post_tag,
                        backref=db.backref('posts', lazy='dynamic'),
                        lazy='dynamic')
                        
    categories = db.relationship('Category',
                        secondary=post_category,
                        backref=db.backref('posts', lazy='dynamic'),
                        lazy='dynamic')
    
    #subsite e.g. ipchimp, ra, t
    subsite = db.Column(db.String(25))
    
    def make_nicename(self):
        """Generate the nicename from the display title"""
        no_punct = re.sub(r'[^\w\s]', '', self.display_title.lower().strip())
        self.nicename = re.sub(r'\s+', '-', no_punct)
    
    @staticmethod
    def exists(nicename):
        """ Check if a post with nicename already exists. """
        return Post.query.filter(Post.nicename == nicename).count() > 0
    
    def tag_by_nicename(self, tag_nicename):
        """ Add tag based on nicename. """
        tag = Tag.query.filter(Tag.nicename == tag_nicename).first()
        if tag:
            return self.tag(tag)
    
    def tag(self, tag):
        """ Add passed tag to post."""
        if not self.tagged(tag):
            self.tags.append(tag)
            return self
        
    def untag(self, tag):
        """ Remove passed tag from post."""
        if self.tagged(tag):
            self.tags.remove(tag)
            return self
        
    def tagged(self, tag):
        """ Is tag assigned to post?"""
        return self.tags.filter(post_tag.c.tag_id == tag.id).count() > 0
    
    def categorise_by_nicename(self, cat_nicename):
        """ Add tag based on nicename. """
        category = Category.query.filter(Category.nicename == cat_nicename).first()
        if category:
            return self.categorise(category)
        
    def categorise(self, category):
        """ Add passed category to post."""
        if not self.categorised(category):
            self.categories.append(category)
            return self

    def uncategorise(self, category):
        """ Remove passed category from post."""
        if self.categorised(category):
            self.categories.remove(category)
            return self
        
    def categorised(self, category):
        """ Is category assigned to post? """
        return self.categories.filter(post_category.c.category_id == category.id).count() > 0
        
    def add_author_by_login(self, login):
        """ Add tag based on nicename. """
        author = Author.query.filter(Author.login == login).first()
        if author:
            self.authors.append(author)
            return self
            
    def get_excerpt(self):
        """ Return excerpt if exists; if not create from content. """
        if len(self.excerpt) > 1:
            return self.excerpt
        else:
            try:
                return self.content.splitlines()[0] + "..."
            except:
                return None
    
    
    