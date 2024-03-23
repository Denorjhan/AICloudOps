import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, scoped_session
import dotenv
from .models.base import Base

dotenv.load_dotenv(override=True)

DB_USER = os.getenv('POSTGRES_USER', 'myuser')
DB_PASSWORD = os.getenv('POSTGRES_PASSWORD', 'mypassword')
DB_HOST = os.getenv('DB_HOST', 'localhost')
DB_PORT = os.getenv('DB_PORT', '5432')  
DB_NAME = os.getenv('POSTGRES_DB', 'pg')

# Construct the database URI
DATABASE_URI = f'postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
print(DATABASE_URI)

# Engine creation with connection pooling 
engine = create_engine(DATABASE_URI, echo=True)

# Session factory and scoped session for thread-local session management
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


def init_db():
    inspector = inspect(engine)
    required_tables = {"code_files", "execution_log"}  # Set of all tables required
    existing_tables = set(inspector.get_table_names())

    if not required_tables.issubset(existing_tables):
        from .models import code_files, execution_log # Required for create_all to know what tables to create
        Base.metadata.create_all(bind=engine) # idempotent so multiple calls are safe
