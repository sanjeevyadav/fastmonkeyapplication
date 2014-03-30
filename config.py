import os
from sqlalchemy.ext.declarative import declarative_base
Base = declarative_base()

basedir = os.path.abspath(os.path.dirname(__file__))
CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'
    
SQLALCHEMY_DATABASE_URI = 'postgresql://sanjeev:sanjeev@localhost:5432/app'
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')

