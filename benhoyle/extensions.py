from flask_sqlalchemy import SQLAlchemy
from flask_wtf import CsrfProtect
from flask_login import LoginManager
from flask_cache import Cache

db = SQLAlchemy()
csrf = CsrfProtect()
login_manager = LoginManager()
cache = Cache(config={'CACHE_TYPE': 'simple'})
