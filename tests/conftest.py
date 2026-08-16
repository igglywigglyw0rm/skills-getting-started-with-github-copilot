"""Shared pytest configuration and fixtures for API tests"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def client():
    """Fixture: Provides a TestClient instance for making HTTP requests"""
    return TestClient(app)


@pytest.fixture
def fresh_activities():
    """
    Fixture: Reset activities to a fresh state before each test.
    
    This ensures test isolation by providing a known starting point.
    Automatically used by tests that depend on it.
    """
    # Save original activities state
    original = activities.copy()
    
    # Reset to a clean state for testing
    activities.clear()
    activities.update({
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 3,
            "participants": ["emma@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 2,
            "participants": []
        }
    })
    
    yield activities
    
    # Restore original state after test
    activities.clear()
    activities.update(original)
