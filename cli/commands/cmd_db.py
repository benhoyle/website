import click

from sqlalchemy_utils import database_exists, create_database

from benhoyle.app import create_app
from benhoyle.extensions import db
from benhoyle.blueprints.blog.models import Author

# Create an app context for the database connection.
app = create_app()
db.app = app


@click.group()
def cli():
    """ Run DB related tasks. """
    pass


@click.command()
@click.option('--with-testdb/--no-with-testdb', default=False,
              help='Create a test db too?')
def init(with_testdb):
    """
    Initialize the database.

    :param with_testdb: Create a test database
    :return: None
    """
    db.drop_all()
    db.create_all()

    if with_testdb:
        db_uri = '{0}_test'.format(app.config['SQLALCHEMY_DATABASE_URI'])

        if not database_exists(db_uri):
            create_database(db_uri)

    return None


@click.command()
def seed():
    """
    Seed the database with an initial user.

    :return: User instance
    """
    if User.find_by_identity(app.config['SEED_ADMIN_EMAIL']) is not None:
        return None

    params = {
        'email': app.config['SEED_ADMIN_EMAIL'],
        'password': app.config['SEED_ADMIN_PASSWORD']
    }

    author = Author(**params)
    db.session.add(author)
    db.session.commit()

    return None


@click.command()
@click.option('--with-testdb/--no-with-testdb', default=False,
              help='Create a test db too?')
@click.pass_context
def reset_db(ctx, with_testdb):
    """
    Init and seed automatically.

    :param with_testdb: Create a test database
    :return: None
    """
    ctx.invoke(init, with_testdb=with_testdb)
    ctx.invoke(seed)

    return None


@click.command()
def show_authors():
    """
    Show all registered blog authors in the system

    :return: None
    """

    click.echo("Blog authors registered in the system:")

    for author in Author.query.all():
        click.echo("{0}".format(author)

    return None


@click.command()
@click.argument('login')
@click.argument('password')
def reset_password(login, password):
    """
    Reset the password for an author.

    :param login: login name for the author
    :param password: new password
    :return: User instance
    """

    author = Author.query.filter(Author.login == login).first()
    if author is None:
        return None

    author.save_password(password)
    db.session.add(author)
    db.session.commit()

    return None


cli.add_command(init)
cli.add_command(seed)
cli.add_command(reset_db)
cli.add_command(show_authors)
cli.add_command(reset_password)
