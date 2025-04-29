import pytest
from fastapi import status

@pytest.mark.unit
class TestDestinations:
    def test_create_destination(self, client, admin_auth_header):
        """Test creating a destination by admin"""
        response = client.post(
            "/destinations/",
            headers=admin_auth_header,
            json={
                "name": "New Destination",
                "region": "New Region",
                "country": "New Country",
                "description": "New destination description",
                "latitude": 15.0,
                "longitude": 15.0,
                "image_url": "https://example.com/image.jpg"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "New Destination"
        assert data["region"] == "New Region"
        assert data["country"] == "New Country"
        assert "id" in data

    def test_get_destinations(self, client, test_destination):
        """Test getting all destinations"""
        response = client.get("/destinations/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(d["name"] == "Test Destination" for d in data)

    def test_get_destination_by_id(self, client, test_destination):
        """Test getting a destination by ID"""
        response = client.get(f"/destinations/{test_destination.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test Destination"
        assert data["region"] == "Test Region"
        assert data["country"] == "Test Country"

    def test_update_destination(self, client, test_destination, admin_auth_header):
        """Test updating a destination by admin"""
        response = client.put(
            f"/destinations/{test_destination.id}",
            headers=admin_auth_header,
            json={
                "name": "Updated Destination",
                "region": "Updated Region",
                "country": "Updated Country",
                "description": "Updated description",
                "latitude": 20.0,
                "longitude": 20.0,
                "image_url": "https://example.com/updated.jpg"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Destination"
        assert data["region"] == "Updated Region"
        assert data["country"] == "Updated Country"

    def test_delete_destination(self, client, test_destination, admin_auth_header):
        """Test deleting a destination by admin"""
        response = client.delete(
            f"/destinations/{test_destination.id}",
            headers=admin_auth_header
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's deleted
        response = client.get(f"/destinations/{test_destination.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND