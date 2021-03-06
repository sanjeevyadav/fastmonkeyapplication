import os
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

basedir = os.path.abspath(os.path.dirname(__file__))
CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

#SQLALCHEMY_DATABASE_URI = 'postgresql://sanjeev:sanjeev@localhost:5432/app'
SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_RECORD_QUERIES = True
WHOOSH_BASE = os.path.join(basedir, 'search.db')

# Whoosh does not work on Heroku
WHOOSH_ENABLED = os.environ.get('HEROKU') is None

# slow database query threshold (in seconds)
DATABASE_QUERY_TIMEOUT = 0.5
#SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
