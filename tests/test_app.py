import pytest
from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app)


class TestRootEndpoint:
    def test_root_redirect(self):
        # Arrange: No special setup needed

        # Act: Make GET request to root without following redirects
        response = client.get("/", follow_redirects=False)

        # Assert: Should redirect to /static/index.html
        assert response.status_code == 307  # Temporary redirect
        assert response.headers["location"] == "/static/index.html"


class TestActivitiesEndpoint:
    def test_get_activities(self):
        # Arrange: No special setup needed

        # Act: Make GET request to /activities
        response = client.get("/activities")

        # Assert: Should return 200 and activities dict
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert "Chess Club" in data
        assert "participants" in data["Chess Club"]
        assert data["Chess Club"]["max_participants"] == 12


class TestSignupEndpoint:
    def test_signup_success(self):
        # Arrange: Use an activity with space for new signup
        activity_name = "Soccer Team"
        email = "newstudent@mergington.edu"

        # Act: Make POST request to signup
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert: Should return 200 and success message
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Signed up {email} for {activity_name}" in data["message"]

    def test_signup_duplicate(self):
        # Arrange: Try to signup same email again
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in participants

        # Act: Make POST request to signup
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert: Should return 400 with error message
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "already signed up" in data["detail"]

    def test_signup_invalid_activity(self):
        # Arrange: Use non-existent activity
        activity_name = "NonExistentActivity"
        email = "test@mergington.edu"

        # Act: Make POST request to signup
        response = client.post(f"/activities/{activity_name}/signup?email={email}")

        # Assert: Should return 404 with error message
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]


class TestRemoveParticipantEndpoint:
    def test_remove_participant_success(self):
        # Arrange: First signup a participant to remove
        activity_name = "Art Studio"
        email = "removeme@mergington.edu"
        client.post(f"/activities/{activity_name}/signup?email={email}")  # Signup first

        # Act: Make DELETE request to remove participant
        response = client.delete(f"/activities/{activity_name}/participants?email={email}")

        # Assert: Should return 200 and success message
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert f"Unregistered {email} from {activity_name}" in data["message"]

    def test_remove_participant_not_found(self):
        # Arrange: Try to remove non-existent participant
        activity_name = "Programming Class"
        email = "notsignedup@mergington.edu"

        # Act: Make DELETE request to remove participant
        response = client.delete(f"/activities/{activity_name}/participants?email={email}")

        # Assert: Should return 404 with error message
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Participant not found" in data["detail"]

    def test_remove_participant_invalid_activity(self):
        # Arrange: Use non-existent activity
        activity_name = "InvalidActivity"
        email = "test@mergington.edu"

        # Act: Make DELETE request to remove participant
        response = client.delete(f"/activities/{activity_name}/participants?email={email}")

        # Assert: Should return 404 with error message
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "Activity not found" in data["detail"]