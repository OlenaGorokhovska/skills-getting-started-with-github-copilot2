"""
Shared test fixtures and configuration for FastAPI tests.
Provides TestClient, test app, and sample test data.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    ARRANGE: Provide a TestClient configured with the FastAPI app.
    This fixture is used by all tests to make HTTP requests to the API.
    """
    return TestClient(app)


@pytest.fixture
def test_activities():
    """
    ARRANGE: Provide fresh test data for each test.
    Returns a copy of activities to ensure test isolation and no side effects.
    """
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 3,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": []
        }
    }


@pytest.fixture(autouse=True)
def reset_app_state(test_activities):
    """
    ARRANGE: Reset app state before each test to ensure test isolation.
    Replaces the activities dict with fresh test data.
    """
    from src import app as app_module
    app_module.activities = test_activities.copy()
    # Deep copy to ensure nested lists don't interfere
    for activity_name, activity_data in app_module.activities.items():
        app_module.activities[activity_name]["participants"] = activity_data["participants"].copy()
