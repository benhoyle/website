# == IMPORTS =============================================================#
import datetime
import unittest
import os

#from .context import app, db, Post, Tag, Category, Author


from website import app, db

from website.models import Post, Tag, Category, Author

from website.parser import WPParser, WPFlaskParser


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



if __name__ == '__main__':
    try:
        unittest.main()
    except:
        pass

