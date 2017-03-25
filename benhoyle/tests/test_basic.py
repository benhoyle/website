import datetime
import pytest
from flask import url_for

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


def add_test_records(session):
    """
    Add a set of test records.

    :param session: DB session
    :return: None
    """
    test_author = Author(
                            login="test1",
                            email="test@testing.com",
                            display_name="Test User 1",
                            first_name="Test",
                            last_name="User 1"
                        )
    test_tag1 = Tag(
        nicename="testtag1",
        display_name="Test Tag 1",
        subsite="Test1"
        )
    test_tag2 = Tag(
        nicename="testtag2",
        display_name="Test Tag 2",
        subsite="Test1"
        )
    test_category = Category(
        nicename="testcat",
        display_name="Test Category",
        subsite="Test1"
        )

    session.add(test_author)
    session.add(test_tag1)
    session.add(test_tag2)
    session.add(test_category)
    session.commit()

    test_post = Post(
        display_title="Test Post",
        nicename="test-post",
        content="This is a test post",
        date_published=datetime.datetime.now(),
        status="published",
        subsite="Test1"
    )
    session.add(test_post)
    session.commit()

    test_post.tag(test_tag1)
    test_post.tag(test_tag2)
    test_post.categorise(test_category)

    session.commit()

    return None


class TestCase(ViewTestMixin):
    """Main test cases."""

    def test_post(self):
        """Check loading and generating a post DB object."""
        add_test_records(self.session)

        test_post = Post.query.first()

        assert test_post.nicename == 'test-post'
        assert test_post.tags.count() == 2
        assert test_post.categories.count() == 1
        assert test_post.categories.first().nicename == "testcat"


class TestOAReview(ViewTestMixin):

    def top_navbar(self, response_data, subsites):
            """ Test top navbar is present based on response data. """
            for subsite in subsites:
                assert subsite in str(response_data)

    def next_navbar(self, response_data):
        """ Check for next level navbar. """
        assert "Posts" in str(response_data)
        assert "Categories" in str(response_data)
        assert "Tags" in str(response_data)

    def test_index(self):
        """ Home page should respond with a success 200. """
        response = self.client.get(url_for('blog.index'))
        assert response.status_code == 200
        assert "ben hoyle" in str(response.data)

    def test_blog_home(self):
        """ Test blog wall for each subsite. """

        subsites = [
            result[0] for result in
            self.session.query(Post.subsite).distinct().all()
        ]

        for subsite in subsites:
            response = self.client.get(
                url_for('blog.post_wall'),
                subsite=subsite
                )
            assert response.status_code == 200

            # Test navbars are displaying
            self.top_navbar(response.data, subsites)
            self.next_navbar(response.data)

            # Test at least one post is displaying
            post = Post.query.filter(
                Post.subsite == subsite).filter(
                    Post.status == "publish").first()
            assert post.display_title in str(response.data)

    def test_categories(self):
        """ Test Categories page. """
        subsites = [
            result[0] for result in
            self.session.query(Post.subsite).distinct().all()
        ]

        for subsite in subsites:
            response = self.client.get(
                url_for('blog.show_categories'),
                subsite=subsite
                )
            assert response.status_code == 200

            # Test navbars are displaying
            self.top_navbar(response.data, subsites)
            self.next_navbar(response.data)

            # Test at least one category is displaying
            category = Category.query.filter(
                Category.subsite == subsite).first()
            assert category.display_name in str(response.data)

    def test_tags(self):
        """ Test Tags page. """
        subsites = [
            result[0] for result in
            self.session.query(Post.subsite).distinct().all()
        ]

        for subsite in subsites:
            response = self.client.get(
                url_for('blog.show_tags'),
                subsite=subsite
                )
            assert response.status_code == 200

            # Test navbars are displaying
            self.top_navbar(response.data, subsites)
            self.next_navbar(response.data)

            # Test at least one category is displaying
            tag = Tag.query.filter(
                Tag.subsite == subsite).first()
            assert tag.display_name in str(response.data)
