"""
This module contains utilities for making PostgreSQL features work with SQLite in tests.
"""
from sqlalchemy import JSON, DateTime, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.types import TypeDecorator
import uuid
from datetime import datetime

TestBase = declarative_base()

# Create SQLite-compatible UUID type
class SQLiteUUID(TypeDecorator):
    """Enables UUID storage in SQLite by storing as string."""
    impl = String(36)
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        return uuid.UUID(value)

def patch_postgresql_types():
    """
    Monkey patch PostgreSQL-specific types to use SQLite-compatible types during testing.
    This allows us to run tests with SQLite (which is faster for tests) without needing
    a full PostgreSQL instance.
    """
    # Override JSONB with regular JSON for SQLite compatibility
    # This is a monkey patch of the SQLAlchemy JSONB type
    original_jsonb_init = JSONB.__init__
    
    def patched_jsonb_init(self, *args, **kwargs):
        original_jsonb_init(self, *args, **kwargs)
        # For SQLite, treat JSONB as TEXT (through JSON type)
        self.__class__ = JSON
        
    JSONB.__init__ = patched_jsonb_init
    
    # For UUID type, we don't directly patch the class,
    # instead we'll use a global function to substitute UUID columns
    # with our SQLiteUUID type in model definitions
    
    # We'll do this by modifying the Column creation for UUID types
    original_column = UUID.__init__
    
    def patched_uuid_init(self, *args, **kwargs):
        # Call the original init but use our SQLite type under the hood
        original_column(self, *args, **kwargs)
        # Don't modify __class__, instead modify internal impl type
        self.impl = SQLiteUUID.impl
    
    UUID.__init__ = patched_uuid_init