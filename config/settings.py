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
