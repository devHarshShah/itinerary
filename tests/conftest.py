import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from jose import jwt
from datetime import datetime, timedelta, timezone

# Import our SQLite compatibility utility
from tests.utils.sqlite_compat import patch_postgresql_types

# Apply the SQLite compatibility patches before importing the models
patch_postgresql_types()

from src.database import get_db, Base
from src.main import app
from src.auth.models import User, UserRole
from src.auth.service import get_password_hash, create_access_token, get_current_user, is_admin
from src.models import Accommodation, Activity, Transfer, Destination
from src.models import AccommodationType, ActivityCategory, TransportType, Itinerary

# Define a fixed SECRET_KEY for testing to ensure consistent token verification
TEST_SECRET_KEY = "test-secret-key-for-testing-only"

# Use in-memory SQLite for tests
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

@pytest.fixture(scope="session")
def test_db_engine():
    """Creates a test database engine."""
    # Create SQLite engine
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    yield engine
    
    # Drop all tables after tests
    Base.metadata.drop_all(bind=engine)
    
@pytest.fixture(scope="function")
def db_session(test_db_engine):
    """Creates a fresh database session for each test."""
    connection = test_db_engine.connect()
    transaction = connection.begin()
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=connection)
    session = TestingSessionLocal()
    
    yield session
    
    session.close()
    transaction.rollback()
    connection.close()

def create_test_token(data: dict, secret_key: str = TEST_SECRET_KEY):
    """Create a test JWT token"""
    to_encode = data.copy()
    # Set a far future expiration for test tokens
    expire = datetime.now(timezone.utc) + timedelta(days=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, secret_key, algorithm="HS256")

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with dependency overrides."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        """Override authentication to provide a test user without real token validation"""
        user = User(
            id=1,
            email="testuser@example.com",
            first_name="Test",
            last_name="User",
            hashed_password=get_password_hash("password123"),
            role=UserRole.USER,
            is_active=True
        )
        return user

    def override_is_admin():
        """Override admin authentication"""
        user = User(
            id=1,
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        return user
            
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[is_admin] = override_is_admin
    
    with TestClient(app) as test_client:
        print("Starting up the API server...")
        yield test_client
        print("Shutting down the API server...")
    
    app.dependency_overrides.clear()

@pytest.fixture
def unauthenticated_client(db_session):
    """Create a test client that doesn't override authentication for testing unauthorized access"""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
            
    # Only override the DB dependency, not the auth dependencies
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        print("Starting up the API server without auth overrides...")
        yield test_client
        print("Shutting down the API server...")
    
    app.dependency_overrides.clear()

@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user."""
    user = User(
        email="testuser@example.com",
        first_name="Test",
        last_name="User",
        hashed_password=get_password_hash("password123"),
        role=UserRole.USER,
        is_active=True
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_admin(db_session):
    """Create a test admin user."""
    admin = User(
        email="admin@example.com",
        first_name="Admin",
        last_name="User",
        hashed_password=get_password_hash("admin123"),
        role=UserRole.ADMIN,
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin

@pytest.fixture(scope="function")
def user_token(test_user):
    """Generate a token for the test user using the test secret key."""
    access_token = create_test_token(
        data={"sub": test_user.email, "user_id": test_user.id}
    )
    return access_token

@pytest.fixture(scope="function")
def admin_token(test_admin):
    """Generate a token for the admin user using the test secret key."""
    access_token = create_test_token(
        data={"sub": test_admin.email, "user_id": test_admin.id}
    )
    return access_token

@pytest.fixture(scope="function")
def auth_header(user_token):
    """Create an authorization header with the user token."""
    return {"Authorization": f"Bearer {user_token}"}

@pytest.fixture(scope="function")
def admin_auth_header(admin_token):
    """Create an authorization header with the admin token."""
    return {"Authorization": f"Bearer {admin_token}"}

@pytest.fixture(scope="function")
def test_destination(db_session):
    """Create a test destination."""
    destination = Destination(
        name="Test Destination",
        region="Test Region",
        country="Test Country",
        description="Test description",
        latitude=10.0,
        longitude=10.0
    )
    db_session.add(destination)
    db_session.commit()
    db_session.refresh(destination)
    return destination

@pytest.fixture(scope="function")
def test_destination_second(db_session):
    """Create a second test destination."""
    destination = Destination(
        name="Second Test Destination",
        region="Second Test Region",
        country="Test Country",
        description="Second test description",
        latitude=20.0,
        longitude=20.0
    )
    db_session.add(destination)
    db_session.commit()
    db_session.refresh(destination)
    return destination

@pytest.fixture(scope="function")
def test_accommodation(db_session, test_destination):
    """Create a test accommodation."""
    accommodation = Accommodation(
        name="Test Accommodation",
        destination_id=test_destination.id,
        type=AccommodationType.HOTEL,
        description="Test description",
        address="Test address",
        stars=4,
        price_category=3,
        amenities={"wifi": True, "pool": True}
    )
    db_session.add(accommodation)
    db_session.commit()
    db_session.refresh(accommodation)
    return accommodation

@pytest.fixture(scope="function")
def test_activity(db_session, test_destination):
    """Create a test activity."""
    activity = Activity(
        name="Test Activity",
        destination_id=test_destination.id,
        category=ActivityCategory.SIGHTSEEING,
        description="Test description",
        duration_hours=2.0,
        price_range="$$",  # Changed from price_category to price_range
        is_must_see=True
    )
    db_session.add(activity)
    db_session.commit()
    db_session.refresh(activity)
    return activity

@pytest.fixture(scope="function")
def test_transfer(db_session, test_destination, test_destination_second):
    """Create a test transfer."""
    transfer = Transfer(
        name="Test Transfer",
        origin_id=test_destination.id,
        destination_id=test_destination_second.id,  # Use different destination
        type=TransportType.TAXI,
        description="Test description",
        duration_hours=1.0,
        price_range="$$"
    )
    db_session.add(transfer)
    db_session.commit()
    db_session.refresh(transfer)
    return transfer

@pytest.fixture(scope="function")
def test_itinerary(db_session):
    """Create a test itinerary."""
    itinerary = Itinerary(
        title="Test Itinerary",
        # Removed user_id field as it's not in the model
        duration_nights=3,
        description="Test description",
        is_recommended=True,
        preferences={"beach": True, "nature": True}
    )
    db_session.add(itinerary)
    db_session.commit()
    db_session.refresh(itinerary)
    return itinerary

@pytest.fixture
def admin_client(db_session):
    """Create a test client with admin user dependency override."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    def override_get_current_user():
        """Override authentication to provide an admin user"""
        user = User(
            id=1,
            email="admin@example.com",
            first_name="Admin",
            last_name="User",
            hashed_password=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        return user
            
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user
    app.dependency_overrides[is_admin] = override_get_current_user  # Use same admin user for is_admin
    app.dependency_overrides["is_authenticated"] = override_get_current_user  # Also override is_authenticated
    
    with TestClient(app) as test_client:
        print("Starting up the API server with admin user...")
        yield test_client
        print("Shutting down the API server...")
    
    app.dependency_overrides.clear()