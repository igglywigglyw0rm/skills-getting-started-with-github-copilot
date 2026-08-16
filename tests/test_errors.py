"""Tests for error handling and edge cases using AAA pattern"""

import pytest


class TestErrorHandling:
    """Test suite for error cases and edge cases"""
    
    def test_signup_with_special_characters_in_activity_name(self, client, fresh_activities):
        """
        Arrange: Prepare request with special characters in activity name
        Act: Submit signup to activity with special characters
        Assert: Request handles special characters safely (404 or 200 depending on encoding)
        """
        # Arrange
        activity_name = "Activity'; DROP TABLE activities--"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        # Should either return 404 (not found) or succeed safely
        # The important thing is it doesn't crash or execute SQL
        assert response.status_code in [200, 404]
    
    def test_signup_with_empty_activity_name(self, client, fresh_activities):
        """
        Arrange: Prepare request with empty activity name
        Act: Submit signup with empty activity name
        Assert: Server handles gracefully
        """
        # Arrange
        activity_name = ""
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response.status_code in [404, 405]
    
    def test_signup_with_missing_email_parameter(self, client, fresh_activities):
        """
        Arrange: Prepare request without email parameter
        Act: Submit signup without email
        Assert: Request fails appropriately
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity_name}/signup")
        
        # Assert
        assert response.status_code == 422  # Unprocessable Entity
    
    def test_signup_with_invalid_email_format(self, client, fresh_activities):
        """
        Arrange: Prepare request with invalid email format
        Act: Submit signup with invalid email
        Assert: Request is processed (app doesn't validate email format currently)
        """
        # Arrange
        activity_name = "Chess Club"
        email = "not-an-email"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Assert
        # Current implementation accepts any string as email
        assert response.status_code == 200
    
    def test_activity_name_case_sensitivity(self, client, fresh_activities):
        """
        Arrange: Test with different case variations
        Act: Signup to 'chess club' (lowercase) vs 'Chess Club' (original case)
        Assert: Activity name is case-sensitive
        """
        # Arrange
        correct_name = "Chess Club"
        wrong_case = "chess club"
        email = "student@mergington.edu"
        
        # Act
        response_correct = client.post(
            f"/activities/{correct_name}/signup",
            params={"email": email}
        )
        response_wrong = client.post(
            f"/activities/{wrong_case}/signup",
            params={"email": email}
        )
        
        # Assert
        assert response_correct.status_code == 200
        assert response_wrong.status_code == 404
    
    def test_unregister_with_missing_email_parameter(self, client, fresh_activities):
        """
        Arrange: Prepare unregister request without email
        Act: Submit unregister without email parameter
        Assert: Request fails with validation error
        """
        # Arrange
        activity_name = "Chess Club"
        
        # Act
        response = client.post(f"/activities/{activity_name}/unregister")
        
        # Assert
        assert response.status_code == 422


class TestResponseFormats:
    """Test suite for response format consistency"""
    
    def test_error_response_includes_detail_field(self, client, fresh_activities):
        """
        Arrange: Prepare request that will fail
        Act: Submit invalid signup request
        Assert: Error response includes 'detail' field with error message
        """
        # Arrange
        activity_name = "Nonexistent"
        email = "student@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert "detail" in data
        assert isinstance(data["detail"], str)
    
    def test_success_response_includes_message_field(self, client, fresh_activities):
        """
        Arrange: Prepare valid signup request
        Act: Submit signup
        Assert: Success response includes 'message' field
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        data = response.json()
        
        # Assert
        assert "message" in data
        assert isinstance(data["message"], str)
    
    def test_activities_response_is_dict(self, client, fresh_activities):
        """
        Arrange: Fetch activities
        Act: Get /activities response
        Assert: Response is a dictionary, not a list
        """
        # Arrange
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert isinstance(data, dict)
        for activity_name, activity_data in data.items():
            assert isinstance(activity_name, str)
            assert isinstance(activity_data, dict)


class TestDataPersistence:
    """Test suite for data persistence across requests"""
    
    def test_signup_persists_across_requests(self, client, fresh_activities):
        """
        Arrange: Sign up a student
        Act: Make multiple GET requests after signup
        Assert: Student appears in all subsequent requests
        """
        # Arrange
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        
        # Act multiple times
        for _ in range(3):
            response = client.get("/activities")
            activities = response.json()
            # Assert after each GET
            assert email in activities[activity_name]["participants"]
    
    def test_multiple_operations_maintain_data_integrity(self, client, fresh_activities):
        """
        Arrange: Original state with some participants
        Act: Sign up new student, unregister original, verify state
        Assert: All operations maintain consistent state
        """
        # Arrange
        activity_name = "Chess Club"
        original_student = "michael@mergington.edu"
        new_student = "alice@mergington.edu"
        
        # Act - Sign up new student
        client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_student}
        )
        
        # Act - Unregister original student
        client.post(
            f"/activities/{activity_name}/unregister",
            params={"email": original_student}
        )
        
        # Act - Verify final state
        response = client.get("/activities")
        participants = response.json()[activity_name]["participants"]
        
        # Assert
        assert original_student not in participants
        assert new_student in participants
