import pytest
from fastapi import status

@pytest.mark.unit
class TestItineraries:
    def test_create_itinerary(self, client, auth_header, test_destination):
        """Test creating an itinerary"""
        response = client.post(
            "/itineraries/",
            headers=auth_header,
            json={
                "title": "New Test Itinerary",
                "duration_nights": 5,
                "description": "A new test itinerary",
                "is_recommended": False,
                "preferences": {"beach": True, "nightlife": True},
                "total_estimated_cost": 15000.0
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["title"] == "New Test Itinerary"
        assert data["duration_nights"] == 5
        assert data["description"] == "A new test itinerary"
        assert "id" in data

    def test_get_itineraries(self, client, test_itinerary, auth_header):
        """Test getting all itineraries"""
        response = client.get("/itineraries/", headers=auth_header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(d["title"] == "Test Itinerary" for d in data)

    def test_get_itinerary_by_id(self, client, test_itinerary, auth_header):
        """Test getting an itinerary by ID"""
        response = client.get(f"/itineraries/{test_itinerary.id}", headers=auth_header)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Test Itinerary"
        assert data["duration_nights"] == 3
        assert "days" in data

    def test_update_itinerary(self, client, test_itinerary, auth_header):
        """Test updating an itinerary"""
        response = client.put(
            f"/itineraries/{test_itinerary.id}",
            headers=auth_header,
            json={
                "title": "Updated Itinerary",
                "duration_nights": 4,
                "description": "Updated description",
                "is_recommended": True,
                "preferences": {"adventure": True, "nature": True},
                "total_estimated_cost": 20000.0
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["title"] == "Updated Itinerary"
        assert data["duration_nights"] == 4

    def test_delete_itinerary(self, client, test_itinerary, auth_header):
        """Test deleting an itinerary"""
        response = client.delete(
            f"/itineraries/{test_itinerary.id}",
            headers=auth_header
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's deleted
        response = client.get(f"/itineraries/{test_itinerary.id}", headers=auth_header)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_get_recommended_itineraries(self, client, test_itinerary):
        """Test getting recommended itineraries"""
        # Update the test itinerary to be recommended
        response = client.get("/itineraries/recommended")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)