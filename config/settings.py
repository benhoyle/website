import os
from datetime import timedelta

BASE_DIR = os.path.split(
    os.path.abspath(os.path.dirname(__file__))
    )[0]

LOG_LEVEL = 'INFO'

# SQLAlchemy.
SQLALCHEMY_DATABASE_URI  = (
    'sqlite:///' + BASE_DIR + '/benhoyle/db/website.db'
    )
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Cookie Settings
REMEMBER_COOKIE_DURATION = timedelta(days=90)

# Mail Settings
MAIL_DEFAULT_SENDER = 'contact@local.host'
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USE_SSL = False
MAIL_USERNAME = 'you@gmail.com'
MAIL_PASSWORD = 'awesomepassword'
