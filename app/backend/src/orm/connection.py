from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from models import Base  # Make sure to import your Base from models.py

DATABASE_URI = 'postgresql+psycopg2://user:password@localhost/dbname'

engine = create_engine(DATABASE_URI, echo=True)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def init_db():
    Base.metadata.create_all(engine)
