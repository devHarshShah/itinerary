import os
import psycopg2
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

load_dotenv()

# PostgreSQL connection parameters
db_host = os.getenv("DB_HOST")
db_name = os.getenv("DB_NAME")
db_user = os.getenv("DB_USER")
db_password = os.getenv("DB_PASSWORD")

# Direct psycopg2 connection (keeping for compatibility)
conn_string = f"host='{db_host}' dbname='{db_name}' user='{db_user}' password='{db_password}'"
conn = psycopg2.connect(conn_string)

# SQLAlchemy connection
SQLALCHEMY_DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}/{db_name}"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Create declarative base for models
Base = declarative_base()

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Context manager for database sessions
@contextmanager
def get_db():
    """Provide a transactional scope around a series of operations."""
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

# Function to initialize database
def init_db():
    """Initialize the database schema."""
    from models import Base
    Base.metadata.create_all(bind=engine)
    print("Database tables created.")

# Function to drop all tables
def drop_db():
    """Drop all database tables."""
    from models import Base
    Base.metadata.drop_all(bind=engine)
    print("Database tables dropped.")
