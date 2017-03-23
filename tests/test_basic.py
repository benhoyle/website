import datetime
import pytest
from flask import url_for

from benhoyle.extensions import db

from benhoyle.blueprints.blog.models import Post, Tag, Category, Author


class ViewTestMixin(object):
    """
    Automatically load in a session and client, this is common for a lot of
    tests that work with views.
    """

    @pytest.fixture(autouse=True)
    def set_common_fixtures(self, session, client):
        self.session = session
        self.client = client

    def login(self, identity='admin@local.host', password='password'):
        """
        Login a specific user.

        :return: Flask response
        """
        return login(self.client, identity, password)

    def logout(self):
        """
        Logout a specific user.

        :return: Flask response
        """
        return logout(self.client)


def login(client, username='', password=''):
    """
    Log a specific user in.

    :param client: Flask client
    :param username: The username
    :type username: str
    :param password: The password
    :type password: str
    :return: Flask response
    """
    user = dict(identity=username, password=password)

    response = client.post(url_for('blog.login'), data=user,
                           follow_redirects=True)

    return response


def logout(client):
    """
    Log a specific user out.

    :param client: Flask client
    :return: Flask response
    """
    return client.get(url_for('blog.logout'), follow_redirects=True)


class TestCase(ViewTestMixin):
    """Main test cases."""

    def test_post(self):
        """Check loading and generating a post DB object."""
        test_author = Author(
                                login="test1",
                                email="test@testing.com",
                                display_name="Test User 1",
                                first_name="Test",
                                last_name="User 1"
                            )
        test_tag1 = Tag(nicename="testtag1", display_name="Test Tag 1")
        test_tag2 = Tag(nicename="testtag2", display_name="Test Tag 2")
        test_category = Category(
            nicename="testcat",
            display_name="Test Category"
            )

        self.session.add(test_author)
        self.session.add(test_tag1)
        self.session.add(test_tag2)
        self.session.add(test_category)
        self.session.commit()

        test_post = Post(
            display_title="Test Post",
            nicename="test-post",
            content="This is a test post",
            date_published=datetime.datetime.now(),
            status="published"
        )
        self.session.add(test_post)
        self.session.commit()

        test_post.tag(test_tag1)
        test_post.tag(test_tag2)
        test_post.categorise(test_category)

        self.session.commit()

        assert test_post.nicename == 'test-post'
        assert test_post.tags.count() == 2
        assert test_post.categories.count() == 1
        assert test_post.categories.first().nicename == "testcat"

class TestOAReview(ViewTestMixin):
    def test_index(self):
        """ Home page should respond with a success 200. """
        response = self.client.get(url_for('blog.index'))
        assert response.status_code == 200

