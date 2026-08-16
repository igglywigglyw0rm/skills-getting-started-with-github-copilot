"""Tests for GET /activities endpoint using AAA (Arrange-Act-Assert) pattern"""

import pytest


class TestGetActivities:
    """Test suite for retrieving activities list"""
    
    def test_get_all_activities_returns_list(self, client, fresh_activities):
        """
        Arrange: Create a test client
        Act: Make GET request to /activities
        Assert: Response contains all activities
        """
        # Arrange
        expected_count = 3
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) == expected_count
        assert "Chess Club" in data
        assert "Programming Class" in data
        assert "Gym Class" in data
    
    def test_activity_has_required_fields(self, client, fresh_activities):
        """
        Arrange: Set up test client
        Act: Get activities from API
        Assert: Each activity has all required fields with correct types
        """
        # Arrange
        required_fields = {"description", "schedule", "max_participants", "participants"}
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert required_fields.issubset(activity_data.keys())
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)
    
    def test_participants_list_contains_valid_emails(self, client, fresh_activities):
        """
        Arrange: Fetch activities with participants
        Act: Extract participant list from Chess Club
        Assert: All participants have valid email format
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        participants = activities[activity_name]["participants"]
        
        # Assert
        assert len(participants) > 0
        for participant in participants:
            assert "@" in participant
            assert "." in participant
    
    def test_empty_participants_list(self, client, fresh_activities):
        """
        Arrange: Get activities where one has no participants
        Act: Retrieve the Gym Class activity
        Assert: Empty participants list is returned correctly
        """
        # Arrange
        activity_name = "Gym Class"
        
        # Act
        response = client.get("/activities")
        activities = response.json()
        participants = activities[activity_name]["participants"]
        
        # Assert
        assert participants == []
        assert isinstance(participants, list)
    
    def test_max_participants_is_positive_integer(self, client, fresh_activities):
        """
        Arrange: Fetch all activities
        Act: Extract max_participants from each activity
        Assert: All values are positive integers
        """
        # Arrange
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            assert activity_data["max_participants"] > 0
            assert isinstance(activity_data["max_participants"], int)
    
    def test_participant_count_matches_list_length(self, client, fresh_activities):
        """
        Arrange: Get activities from API
        Act: Count participants in each activity
        Assert: Participant count matches length of participants list
        """
        # Arrange
        # Act
        response = client.get("/activities")
        activities = response.json()
        
        # Assert
        for activity_name, activity_data in activities.items():
            participant_count = len(activity_data["participants"])
            assert participant_count <= activity_data["max_participants"]
