import pytest
from fastapi import status
from src.models import ActivityCategory

@pytest.mark.unit
class TestActivities:
    def test_create_activity(self, client, auth_header, test_destination):
        """Test creating an activity"""
        response = client.post(
            "/activities/",
            headers=auth_header,
            json={
                "name": "New Test Activity",
                "destination_id": test_destination.id,
                "category": "sightseeing",
                "description": "A new test activity",
                "location": "Test Location",
                "duration_hours": 3.0,
                "price_category": 2,
                "is_must_see": True,
                "recommended_time_of_day": "MORNING",
                "image_url": "https://example.com/activity.jpg",
                "contact_info": {"phone": "123-456-7890", "email": "activity@example.com"},
                "additional_info": "Some additional information about the activity"
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "New Test Activity"
        assert data["category"] == "sightseeing"
        assert data["is_must_see"] == True
        assert "id" in data

    def test_get_activities(self, client, test_activity):
        """Test getting all activities"""
        response = client.get("/activities/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(a["name"] == "Test Activity" for a in data)

    def test_filter_activities(self, client, test_activity, test_destination):
        """Test filtering activities by destination and must-see status"""
        response = client.get(f"/activities/?destination_id={test_destination.id}&is_must_see=true")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert all(a["destination_id"] == test_destination.id for a in data)
        assert all(a["is_must_see"] == True for a in data)

    def test_get_activity_by_id(self, client, test_activity):
        """Test getting an activity by ID"""
        response = client.get(f"/activities/{test_activity.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test Activity"
        assert data["category"] == "sightseeing"

    def test_update_activity(self, client, test_activity, auth_header):
        """Test updating an activity"""
        response = client.put(
            f"/activities/{test_activity.id}",
            headers=auth_header,
            json={
                "name": "Updated Activity",
                "destination_id": test_activity.destination_id,
                "category": "adventure",
                "description": "Updated description",
                "location": "Updated Location",
                "duration_hours": 4.0,
                "price_category": 3,
                "is_must_see": False,
                "recommended_time_of_day": "AFTERNOON",
                "image_url": "https://example.com/updated-activity.jpg",
                "contact_info": {"phone": "987-654-3210", "email": "updated@example.com"},
                "additional_info": "Updated additional information"
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Activity"
        assert data["category"] == "adventure"
        assert data["is_must_see"] == False

    def test_delete_activity(self, client, test_activity, admin_auth_header):
        """Test deleting an activity by admin"""
        response = client.delete(
            f"/activities/{test_activity.id}",
            headers=admin_auth_header
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's deleted
        response = client.get(f"/activities/{test_activity.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND