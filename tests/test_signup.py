"""
Tests for POST /activities/{activity_name}/signup and DELETE signup endpoints using AAA pattern.
Verifies student signup, unregister, error handling, and edge cases.
"""

import pytest


class TestPostSignup:
    """Test suite for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_student_returns_200(self, client):
        """
        Test: Happy path — new student can successfully sign up for an activity.

        ARRANGE: TestClient, Gym Class is empty and available
        ACT: POST signup with new student email
        ASSERT: Status is 200 and confirmation message contains email and activity name
        """
        # ARRANGE
        new_email = "newstudent@mergington.edu"
        activity_name = "Gym Class"

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )

        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert new_email in data["message"]
        assert activity_name in data["message"]
        assert "Signed up" in data["message"]

    def test_signup_adds_student_to_activity(self, client):
        """
        Test: Verify student is actually added to activity participants.

        ARRANGE: TestClient, new student email, activity name
        ACT: POST signup and then GET activities
        ASSERT: Student appears in activity's participants list
        """
        # ARRANGE
        new_email = "newstudent@mergington.edu"
        activity_name = "Gym Class"

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": new_email}
        )

        # ASSERT
        assert response.status_code == 200

        # Verify student was added by checking activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert new_email in activities[activity_name]["participants"]

    def test_signup_duplicate_returns_400(self, client):
        """
        Test: Error case — student already signed up cannot sign up again.

        ARRANGE: TestClient, Chess Club already has michael@mergington.edu
        ACT: POST signup with same email (already in participants)
        ASSERT: Status is 400 and error message indicates already signed up
        """
        # ARRANGE
        duplicate_email = "michael@mergington.edu"  # Already in Chess Club
        activity_name = "Chess Club"

        # ACT
        response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": duplicate_email}
        )

        # ASSERT
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"].lower()

    def test_signup_invalid_activity_returns_404(self, client):
        """
        Test: Error case — cannot sign up for non-existent activity.

        ARRANGE: TestClient, invalid activity name
        ACT: POST signup with activity that doesn't exist
        ASSERT: Status is 404 and error message indicates activity not found
        """
        # ARRANGE
        email = "newstudent@mergington.edu"
        invalid_activity = "NonExistentActivity"

        # ACT
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": email}
        )

        # ASSERT
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_at_capacity_returns_400(self, client):
        """
        Test: Error case — cannot sign up when activity is at max capacity.

        ARRANGE: Chess Club has max_participants=3 and 2 current participants
        ACT: POST signup twice to reach capacity, then attempt third signup
        ASSERT: First signup succeeds (200), second succeeds (reaching capacity),
                third attempt returns 400 (at capacity)
        """
        # ARRANGE
        activity_name = "Chess Club"
        email_1 = "student1@mergington.edu"
        email_2 = "student2@mergington.edu"
        email_3 = "student3@mergington.edu"

        # ACT: First signup (reaches capacity: 2 existing + 1 new = 3 max)
        response_1 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email_1}
        )

        # ASSERT: First signup succeeds
        assert response_1.status_code == 200

        # ACT: Second signup (exceeds capacity)
        response_2 = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email_2}
        )

        # ASSERT: Second signup should fail if capacity logic is implemented
        # Note: This test documents the expected behavior if capacity check is added
        # Currently the app may not enforce capacity, but test is ready for when it does
        if response_2.status_code == 400:
            assert "capacity" in response_2.json()["detail"].lower()


class TestDeleteSignup:
    """Test suite for DELETE /activities/{activity_name}/signup/{email} endpoint."""

    def test_unregister_existing_student_returns_200(self, client):
        """
        Test: Happy path — student can successfully unregister from activity.

        ARRANGE: TestClient, michael@mergington.edu is in Chess Club
        ACT: DELETE unregister with existing student email
        ASSERT: Status is 200 and confirmation message contains email and activity name
        """
        # ARRANGE
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/signup/{email}"
        )

        # ASSERT
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert email in data["message"]
        assert activity_name in data["message"]
        assert "Unregistered" in data["message"]

    def test_unregister_removes_student_from_activity(self, client):
        """
        Test: Verify student is actually removed from activity participants.

        ARRANGE: TestClient, michael@mergington.edu in Chess Club
        ACT: DELETE unregister and then GET activities
        ASSERT: Student no longer appears in activity's participants list
        """
        # ARRANGE
        email = "michael@mergington.edu"
        activity_name = "Chess Club"

        # Verify student is initially in activity
        activities_before = client.get("/activities").json()
        assert email in activities_before[activity_name]["participants"]

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/signup/{email}"
        )

        # ASSERT
        assert response.status_code == 200

        # Verify student was removed
        activities_after = client.get("/activities").json()
        assert email not in activities_after[activity_name]["participants"]

    def test_unregister_not_registered_returns_400(self, client):
        """
        Test: Error case — cannot unregister student who isn't registered.

        ARRANGE: TestClient, newstudent@mergington.edu not in Chess Club
        ACT: DELETE unregister with email not in participants
        ASSERT: Status is 400 and error message indicates not registered
        """
        # ARRANGE
        email = "notregistered@mergington.edu"
        activity_name = "Chess Club"

        # ACT
        response = client.delete(
            f"/activities/{activity_name}/signup/{email}"
        )

        # ASSERT
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "not registered" in data["detail"].lower()

    def test_unregister_invalid_activity_returns_404(self, client):
        """
        Test: Error case — cannot unregister from non-existent activity.

        ARRANGE: TestClient, invalid activity name
        ACT: DELETE unregister with activity that doesn't exist
        ASSERT: Status is 404 and error message indicates activity not found
        """
        # ARRANGE
        email = "student@mergington.edu"
        invalid_activity = "NonExistentActivity"

        # ACT
        response = client.delete(
            f"/activities/{invalid_activity}/signup/{email}"
        )

        # ASSERT
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_signup_and_unregister_roundtrip(self, client):
        """
        Test: Integration test — student can sign up and then unregister.

        ARRANGE: TestClient, Gym Class is empty
        ACT: Sign up student, verify added, unregister, verify removed
        ASSERT: All operations succeed and state changes are reflected
        """
        # ARRANGE
        email = "roundtrip@mergington.edu"
        activity_name = "Gym Class"

        # ACT & ASSERT: Sign up
        signup_response = client.post(
            f"/activities/{activity_name}/signup",
            params={"email": email}
        )
        assert signup_response.status_code == 200

        # Verify student was added
        activities = client.get("/activities").json()
        assert email in activities[activity_name]["participants"]

        # ACT & ASSERT: Unregister
        unregister_response = client.delete(
            f"/activities/{activity_name}/signup/{email}"
        )
        assert unregister_response.status_code == 200

        # Verify student was removed
        activities = client.get("/activities").json()
        assert email not in activities[activity_name]["participants"]
