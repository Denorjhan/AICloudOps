import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


import dotenv
dotenv.load_dotenv(override=True)
# Get database credentials from environment variables
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_HOST = os.getenv('DB_HOST')
DB_PORT = os.getenv('DB_PORT')
DB_NAME = os.getenv('DB_NAME')

DATABASE_URI = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'

engine = create_engine(DATABASE_URI, echo=True)
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)

def init_db():
    #Base.metadata.create_all(engine)
    pass

