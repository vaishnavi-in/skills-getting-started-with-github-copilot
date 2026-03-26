import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


def test_get_activities():
    """Test retrieving all activities"""
    # Arrange - No special setup needed
    
    # Act
    response = client.get("/activities")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    
    # Check structure of an activity
    activity = data["Chess Club"]
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_success():
    """Test successful signup"""
    # Arrange
    email = "test@example.com"
    activity = "Chess Club"
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    
    # Verify the participant was added
    response = client.get("/activities")
    activities = response.json()
    assert email in activities[activity]["participants"]


def test_signup_duplicate():
    """Test signing up for the same activity twice"""
    # Arrange
    email = "dup@example.com"
    activity = "Programming Class"
    client.post(f"/activities/{activity}/signup?email={email}")  # First signup
    
    # Act
    response = client.post(f"/activities/{activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 400
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_invalid_activity():
    """Test signing up for non-existent activity"""
    # Arrange
    email = "test@example.com"
    invalid_activity = "Invalid Activity"
    
    # Act
    response = client.post(f"/activities/{invalid_activity}/signup?email={email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_delete_participant():
    """Test unregistering a participant"""
    # Arrange
    email = "del@example.com"
    activity = "Gym Class"
    client.post(f"/activities/{activity}/signup?email={email}")  # Add participant first
    
    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")
    
    # Assert
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]
    
    # Verify removed
    response = client.get("/activities")
    activities = response.json()
    assert email not in activities[activity]["participants"]


def test_delete_participant_not_found():
    """Test deleting a non-existent participant"""
    # Arrange
    email = "notfound@example.com"
    activity = "Chess Club"
    
    # Act
    response = client.delete(f"/activities/{activity}/participants/{email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Participant not found" in data["detail"]


def test_delete_invalid_activity():
    """Test deleting from non-existent activity"""
    # Arrange
    email = "test@example.com"
    invalid_activity = "Invalid Activity"
    
    # Act
    response = client.delete(f"/activities/{invalid_activity}/participants/{email}")
    
    # Assert
    assert response.status_code == 404
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_root_redirect():
    """Test root path redirects to static index"""
    # Arrange - No special setup needed
    
    # Act
    response = client.get("/", follow_redirects=False)
    
    # Assert
    assert response.status_code == 307  # Temporary redirect
    assert "/static/index.html" in response.headers["location"]