import pytest
from fastapi import status
import json  # Add this import to help with printing the error response

@pytest.mark.integration
class TestItineraryFlow:
    """Integration tests for the complete itinerary creation flow."""
    
    def test_complete_itinerary_flow(self, client, admin_auth_header):
        """Test the complete flow of creating an itinerary with all related components."""
        
        # Step 1: Create a destination
        destination_data = {
            "name": "Integration Test Destination",
            "region": "Test Region",
            "country": "Test Country",
            "description": "A beautiful destination for integration testing",
            "latitude": 12.34,
            "longitude": 56.78,
            "image_url": "https://example.com/destination.jpg"
        }
        
        destination_response = client.post(
            "/destinations/",
            headers=admin_auth_header,
            json=destination_data
        )
        assert destination_response.status_code == status.HTTP_201_CREATED
        destination = destination_response.json()
        destination_id = destination["id"]
        
        # Step 2: Create an accommodation at the destination
        accommodation_data = {
            "name": "Test Resort",
            "destination_id": destination_id,
            "type": "hotel",  # Changed from 'resort' to 'hotel' to match enum values
            "description": "A lovely resort for testing",
            "address": "123 Integration Test Road",
            "stars": 4,
            "price_category": 3,
            "amenities": {"pool": True, "wifi": True, "breakfast": True}
        }
        
        accommodation_response = client.post(
            "/accommodations/",
            headers=admin_auth_header,
            json=accommodation_data
        )
        assert accommodation_response.status_code == status.HTTP_201_CREATED
        accommodation = accommodation_response.json()
        accommodation_id = accommodation["id"]
        
        # Step 3: Create an activity at the destination
        activity_data = {
            "name": "Beach Day",
            "destination_id": destination_id,
            "category": "sightseeing",  # Changed from 'water_activity' to 'sightseeing' to match enum values
            "description": "A relaxing day at the beach",
            "duration_hours": 4.0,
            "price_range": "$$",  # Changed from price_category to price_range
            "is_must_see": True
        }
        
        activity_response = client.post(
            "/activities/",
            headers=admin_auth_header,
            json=activity_data
        )
        assert activity_response.status_code == status.HTTP_201_CREATED
        activity = activity_response.json()
        activity_id = activity["id"]
        
        # Step 4: Create a second destination for transfers
        second_destination_data = {
            "name": "Second Test Destination",
            "region": "Test Region",
            "country": "Test Country",
            "description": "Another destination for testing transfers",
            "latitude": 23.45,
            "longitude": 67.89
        }
        
        second_destination_response = client.post(
            "/destinations/",
            headers=admin_auth_header,
            json=second_destination_data
        )
        assert second_destination_response.status_code == status.HTTP_201_CREATED
        second_destination = second_destination_response.json()
        second_destination_id = second_destination["id"]
        
        # Step 5: Create a transfer between destinations
        transfer_data = {
            "name": "Test Transfer",
            "origin_id": destination_id,
            "destination_id": second_destination_id,
            "type": "taxi",  # Changed from 'ferry' to 'taxi' to match enum values
            "description": "A taxi transfer between test destinations",
            "duration_hours": 2.0,
            "price_range": "$$"  # Changed from price_category to price_range
        }
        
        transfer_response = client.post(
            "/transfers/",
            headers=admin_auth_header,
            json=transfer_data
        )
        assert transfer_response.status_code == status.HTTP_201_CREATED
        transfer = transfer_response.json()
        transfer_id = transfer["id"]
        
        # Step 6: Create an itinerary
        itinerary_data = {
            "title": "Integration Test Itinerary",
            "duration_nights": 3,
            "description": "A test itinerary created during integration testing",
            "is_recommended": True,
            "preferences": {"beach": True, "relaxation": True}
            # Removed total_estimated_cost as it might not be in the schema
        }
        
        itinerary_response = client.post(
            "/itineraries/",
            headers=admin_auth_header,
            json=itinerary_data
        )
        assert itinerary_response.status_code == status.HTTP_201_CREATED
        itinerary = itinerary_response.json()
        itinerary_id = itinerary["id"]
        
        # Step 7: Add a day to the itinerary with accommodation, activity, and transfer
        day_data = {
            "day_number": 1,  # Added the required day_number field
            "main_destination_id": destination_id,
            "description": "First day of our trip",
            "accommodations": [accommodation_id],
            "activities": [
                {
                    "id": activity_id,
                    "start_time": "10:00:00",  # Added seconds to match time format
                    "end_time": "14:00:00",    # Added seconds to match time format
                    "order": 1
                }
            ],
            "transfers": [
                {
                    "id": transfer_id,
                    "order": 1
                }
            ]
        }
        
        day_response = client.post(
            f"/itineraries/{itinerary_id}/days",
            headers=admin_auth_header,
            json=day_data
        )
        
        # Print the error details if we get a 422 response
        if day_response.status_code == 422:
            print("\nValidation error details:")
            print(json.dumps(day_response.json(), indent=2))
            
        assert day_response.status_code == status.HTTP_201_CREATED
        day = day_response.json()
        
        # Step 8: Get the complete itinerary to verify everything was added correctly
        get_itinerary_response = client.get(
            f"/itineraries/{itinerary_id}",
            headers=admin_auth_header
        )
        assert get_itinerary_response.status_code == status.HTTP_200_OK
        complete_itinerary = get_itinerary_response.json()
        
        # Verify that the itinerary contains the expected data
        assert complete_itinerary["title"] == "Integration Test Itinerary"
        assert len(complete_itinerary["days"]) == 1
        assert complete_itinerary["days"][0]["main_destination_id"] == destination_id  # Fixed: using main_destination_id instead of main_destination.id
        assert len(complete_itinerary["days"][0]["accommodations"]) == 1
        assert complete_itinerary["days"][0]["accommodations"][0]["id"] == accommodation_id
        assert len(complete_itinerary["days"][0]["activities"]) == 1
        assert complete_itinerary["days"][0]["activities"][0]["id"] == activity_id
        assert len(complete_itinerary["days"][0]["transfers"]) == 1
        assert complete_itinerary["days"][0]["transfers"][0]["id"] == transfer_id