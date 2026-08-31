"""
Tests for GET /activities endpoint using AAA (Arrange-Act-Assert) pattern.
Verifies that the API returns all activities with correct structure and data.
"""

import pytest


class TestGetActivities:
    """Test suite for GET /activities endpoint."""

    def test_get_all_activities_returns_200(self, client):
        """
        Test: Happy path — returns all activities with 200 status.

        ARRANGE: TestClient is provided by fixture
        ACT: Make GET request to /activities
        ASSERT: Verify status code is 200 and response is not empty
        """
        # ACT
        response = client.get("/activities")

        # ASSERT
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) > 0
        assert "Chess Club" in activities
        assert "Programming Class" in activities
        assert "Gym Class" in activities

    def test_get_activities_response_structure(self, client):
        """
        Test: Verify each activity has correct structure and required fields.

        ARRANGE: TestClient is provided by fixture
        ACT: Make GET request to /activities
        ASSERT: Verify each activity has description, schedule, max_participants, participants
        """
        # ACT
        response = client.get("/activities")

        # ASSERT
        assert response.status_code == 200
        activities = response.json()

        # Verify structure of each activity
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_name, str)
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data

            # Verify field types
            assert isinstance(activity_data["description"], str)
            assert isinstance(activity_data["schedule"], str)
            assert isinstance(activity_data["max_participants"], int)
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_contains_participant_data(self, client):
        """
        Test: Verify that activities contain participant information.

        ARRANGE: TestClient is provided by fixture
        ACT: Make GET request to /activities
        ASSERT: Verify participants list contains expected data
        """
        # ACT
        response = client.get("/activities")

        # ASSERT
        assert response.status_code == 200
        activities = response.json()

        # Chess Club should have 2 participants
        assert len(activities["Chess Club"]["participants"]) == 2
        assert "michael@mergington.edu" in activities["Chess Club"]["participants"]
        assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]

        # Programming Class should have 1 participant
        assert len(activities["Programming Class"]["participants"]) == 1
        assert "emma@mergington.edu" in activities["Programming Class"]["participants"]

        # Gym Class should have 0 participants
        assert len(activities["Gym Class"]["participants"]) == 0
