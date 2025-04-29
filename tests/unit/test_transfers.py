import pytest
from fastapi import status
from src.models import TransportType

@pytest.mark.unit
class TestTransfers:
    def test_create_transfer(self, admin_client, auth_header, test_destination, test_destination_second):
        """Test creating a transfer"""
        response = admin_client.post(
            "/transfers/",
            headers=auth_header,
            json={
                "name": "New Test Transfer",
                "origin_id": test_destination.id,
                "destination_id": test_destination_second.id,  # Use second destination
                "type": "taxi",
                "description": "A new test transfer",
                "duration_hours": 1.5,
                "price_category": 2,
                "provider": "Test Provider",
                "additional_info": "Some additional information about the transfer",
                "contact_info": {"phone": "123-456-7890", "email": "transfer@example.com"}
            }
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "New Test Transfer"
        assert data["type"] == "taxi"
        assert "id" in data

    def test_get_transfers(self, client, test_transfer):
        """Test getting all transfers"""
        response = client.get("/transfers/")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert any(t["name"] == "Test Transfer" for t in data)

    def test_filter_transfers(self, client, test_transfer):
        """Test filtering transfers by type"""
        response = client.get("/transfers/?type=TAXI")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0
        assert all(t["type"] == "taxi" for t in data)

    def test_get_transfer_by_id(self, client, test_transfer):
        """Test getting a transfer by ID"""
        response = client.get(f"/transfers/{test_transfer.id}")
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Test Transfer"
        assert data["type"] == "taxi"

    def test_update_transfer(self, client, test_transfer, auth_header):
        """Test updating a transfer"""
        response = client.put(
            f"/transfers/{test_transfer.id}",
            headers=auth_header,
            json={
                "name": "Updated Transfer",
                "origin_id": test_transfer.origin_id,
                "destination_id": test_transfer.destination_id,
                "type": "ferry",
                "description": "Updated description",
                "duration_hours": 2.0,
                "price_category": 3,
                "provider": "Updated Provider",
                "additional_info": "Updated additional information",
                "contact_info": {"phone": "987-654-3210", "email": "updated@example.com"}
            }
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["name"] == "Updated Transfer"
        assert data["type"] == "ferry"

    def test_delete_transfer(self, client, test_transfer, admin_auth_header):
        """Test deleting a transfer by admin"""
        response = client.delete(
            f"/transfers/{test_transfer.id}",
            headers=admin_auth_header
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # Verify it's deleted
        response = client.get(f"/transfers/{test_transfer.id}")
        assert response.status_code == status.HTTP_404_NOT_FOUND