# == IMPORTS =============================================================#
import datetime
import unittest
import os

#from .context import app, db, Post, Tag, Category, Author


from wordpress_converter import app, db

from wordpress_converter.models import Post, Tag, Category, Author

from wordpress_converter.parser import WPParser, WPFlaskParser


# == /IMPORTS ============================================================#

# == TEST CLASS & METHODS =================================================#
class TestCase(unittest.TestCase):
    """Main test cases."""

    def setUp(self):
        """Pre-test activities."""
        app.config['Testing'] = True
        app.config['HOST'] = '0.0.0.0'
        app.config['PORT'] = 5555
        app.config['WTF_CSRF_ENABLED'] = False
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app = app.test_client()
        db.create_all()
        
        # Setup parsers
        self.flaskparser = WPFlaskParser(os.path.abspath(os.path.join(os.path.dirname(__file__), 'test.xml')))


    def tearDown(self):
        db.session.remove()
        db.drop_all()


    def test_post(self):
        """Check loading and generating a post DB object."""
        test_author = Author(
                                login = "test1",
                                email = "test@testing.com",
                                display_name = "Test User 1",
                                first_name = "Test",
                                last_name = "User 1"
                            )
        test_tag1 = Tag(nicename="testtag1", display_name="Test Tag 1")
        test_tag2 = Tag(nicename="testtag2", display_name="Test Tag 2")
        test_category = Category(nicename="testcat", display_name="Test Category")
        
        db.session.add(test_author)
        db.session.add(test_tag1)
        db.session.add(test_tag2)
        db.session.add(test_category)
        db.session.commit()
        
        test_post = Post(
            display_title = "Test Post",
            nicename = "test-post",
            content = "This is a test post",
            date_published = datetime.datetime.now(),
            status = "published"
        )
        db.session.add(test_post)
        db.session.commit()
        
        test_post.tag(test_tag1)
        test_post.tag(test_tag2)
        test_post.categorise(test_category)
        
        db.session.commit()
        
        assert test_post.nicename == 'test-post'
        assert test_post.tags.count() == 2
        assert test_post.categories.count() == 1
        assert test_post.categories.first().nicename == "testcat"


    def test_parse_tags_categories(self):
        """ Check parsing of tags and categories. """
        self.flaskparser.save_tags()
        self.flaskparser.save_categories()
        
        # Get tags and categories
        tags = Tag.query.all()
        categories = Category.query.all()
        
        assert len(tags) == 2
        assert tags[0].nicename == "test-tag-1"
        assert tags[1].nicename == "testtag2"
        
        assert len(categories) == 2
        assert categories[0].display_name == "Test Category 1"
        assert categories[1].display_name == "Test Category 2"
        
    def test_parse_posts(self):
        """ Check parsing of posts. """
        
        self.flaskparser.save_authors()
        self.flaskparser.save_tags()
        self.flaskparser.save_categories()
        
        self.flaskparser.save_posts()
        
        posts = Post.query.all()
        
        assert len(posts) > 0
        assert len(posts[0].content) > 0
        assert posts[0].tags.count() == 2
        assert posts[0].categories[0].nicename == "testcat1"
        assert posts[0].authors[0].last_name == "Author"


    def test_all_parse(self):
        """ Test all parsing functions. """
        self.flaskparser.save_all()
        posts = Post.query.all()
        
        assert len(posts) > 0
        assert len(posts[0].content) > 0
        assert posts[0].tags.count() == 2
        assert posts[0].categories[0].nicename == "testcat1"
        assert posts[0].authors[0].last_name == "Author"

if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass
   
