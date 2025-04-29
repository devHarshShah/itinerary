import pytest
from fastapi import status
from src.auth.models import UserRole

@pytest.mark.unit
class TestAuth:
    def test_register_user(self, client):
        """Test user registration"""
        response = client.post(
            "/auth/register",
            json={
                "email": "newuser@example.com",
                "first_name": "New",
                "last_name": "User",
                "password": "Password123"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["first_name"] == "New"
        assert data["last_name"] == "User"
        assert "id" in data
        assert "hashed_password" not in data

    def test_login(self, client, test_user):
        """Test user login"""
        # Use JSON instead of form-encoded data for login
        response = client.post(
            "/auth/login",
            json={
                "email": "testuser@example.com", 
                "password": "password123"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client):
        """Test login with invalid credentials"""
        # Use JSON for login credentials
        response = client.post(
            "/auth/login",
            json={
                "email": "testuser@example.com",
                "password": "wrongpassword"
            }
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_current_user(self, client, auth_header):
        """Test getting the current user details"""
        response = client.get("/auth/me", headers=auth_header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == "testuser@example.com"
        assert data["role"] == "user"  # Using actual lowercase enum value

    def test_unauthorized_access(self, unauthenticated_client):
        """Test accessing protected endpoint without token"""
        response = unauthenticated_client.get("/auth/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED