import pytest
from fastapi import status
from src.models import AccommodationType

@pytest.mark.unit
class TestAccommodations:
    def test_create_accommodation(self, client, auth_header, test_destination):
        """Test creating an accommodation"""
        response = client.post(
            "/accommodations/",
            headers=auth_header,
            json={
                "name": "New Test Hotel",
                "destination_id": test_destination.id,
                "type": "hotel",
                "description": "A new test hotel",
                "address": "123 Test Street",
                "stars": 4,
                "price_category": 3,
                "amenities": {"wifi": True, "pool": True, "breakfast": True},
                "website_url": "https://example.com/hotel",
                "image_url": "https://example.com/image.jpg",
                "contact_info": {"phone": "123-456-7890", "email": "hotel@example.com"}
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "New Test Hotel"
        assert data["type"] == "hotel"
        assert data["stars"] == 4
        assert "id" in data

    def test_get_accommodations(self, client, test_accommodation):
        """Test getting all accommodations"""
        response = client.get("/accommodations/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(a["name"] == "Test Accommodation" for a in data)

    def test_filter_accommodations(self, client, test_accommodation, test_destination):
        """Test filtering accommodations by destination"""
        response = client.get(f"/accommodations/?destination_id={test_destination.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert all(a["destination_id"] == test_destination.id for a in data)

    def test_get_accommodation_by_id(self, client, test_accommodation):
        """Test getting an accommodation by ID"""
        response = client.get(f"/accommodations/{test_accommodation.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test Accommodation"
        assert data["type"] == "hotel"

    def test_update_accommodation(self, client, test_accommodation, auth_header):
        """Test updating an accommodation"""
        response = client.put(
            f"/accommodations/{test_accommodation.id}",
            headers=auth_header,
            json={
                "name": "Updated Hotel",
                "destination_id": test_accommodation.destination_id,
                "type": "resort",
                "description": "Updated description",
                "address": "456 Updated Street",
                "stars": 5,
                "price_category": 4,
                "amenities": {"wifi": True, "pool": True, "spa": True},
                "website_url": "https://example.com/updated",
                "image_url": "https://example.com/updated.jpg",
                "contact_info": {"phone": "987-654-3210", "email": "updated@example.com"}
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Hotel"
        assert data["type"] == "resort"
        assert data["stars"] == 5

    def test_delete_accommodation(self, client, test_accommodation, admin_auth_header):
        """Test deleting an accommodation by admin"""
        response = client.delete(
            f"/accommodations/{test_accommodation.id}",
            headers=admin_auth_header
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's deleted
        response = client.get(f"/accommodations/{test_accommodation.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND