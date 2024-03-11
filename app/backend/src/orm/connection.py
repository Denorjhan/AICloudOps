import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base  # Make sure to import your Base from models.py

# Get database credentials from environment variables
DB_USER = os.getenv('DB_USER', 'user')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_NAME = os.getenv('DB_NAME', 'dbname')

DATABASE_URI = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}/{DB_NAME}'

engine = create_engine(DATABASE_URI, echo=True)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def init_db():
    Base.metadata.create_all(engine)
