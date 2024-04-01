import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
import dotenv

from .models import execution_logs
from .models.base import Base

dotenv.load_dotenv(override=True)

DB_USER = os.getenv('POSTGRES_USER')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD')
DB_NAME = os.getenv('POSTGRES_DB')
DB_HOST = os.getenv('DB_HOST') 
DB_PORT = os.getenv('DB_PORT')  

# Construct the database URI
DATABASE_URI = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
print(DATABASE_URI)
# Engine creation with connection pooling 
engine = create_engine(DATABASE_URI, echo=True)
print("Engine created")
# Session factory and scoped session for thread-local session management
session_factory = sessionmaker(bind=engine)
print("Session factory created")
Session = scoped_session(session_factory)
print("Scoped session created")


def init_db():
    print("Initializing database")
    # pass
    inspector = inspect(engine)
    required_tables = {"code_files", "execution_log"}  # Set of all tables required
    existing_tables = set(inspector.get_table_names())
    print("Existing tables: ", existing_tables)

    if not required_tables.issubset(existing_tables):
        print("Creating tables")
        from .models import code_files # Required for create_all to know what tables to create
        Base.metadata.create_all(bind=engine) # idempotent so multiple calls are safe

