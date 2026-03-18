"""Tests for the FastAPI backend (using Arrange-Act-Assert)."""

from fastapi import status


def test_root_redirects_to_static_index(client):
    # Arrange
    expected_location = "/static/index.html"

    # Act
    # Set follow_redirects=False so we can assert the redirect response rather than following it.
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code in (status.HTTP_307_TEMPORARY_REDIRECT, status.HTTP_308_PERMANENT_REDIRECT)
    assert response.headers["location"].endswith(expected_location)


def test_get_activities_returns_all_activities(client):
    # Arrange

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    json_body = response.json()
    assert isinstance(json_body, dict)
    assert "Chess Club" in json_body


def test_signup_for_activity_succeeds_and_adds_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "test@example.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"

    # Verify side effect: the participant was added
    activities_resp = client.get("/activities").json()
    assert email in activities_resp[activity_name]["participants"]


def test_signup_for_activity_fails_when_already_signed_up(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"  # already in the seed data

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Student already signed up"


def test_signup_for_activity_fails_when_activity_not_found(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "test@example.com"

    # Act
    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Activity not found"


def test_unregister_from_activity_succeeds_and_removes_participant(client):
    # Arrange
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    # Verify side effect: the participant was removed
    activities_resp = client.get("/activities").json()
    assert email not in activities_resp[activity_name]["participants"]


def test_unregister_from_activity_fails_when_not_signed_up(client):
    # Arrange
    activity_name = "Chess Club"
    email = "not-registered@example.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "Student not signed up for this activity"


def test_unregister_from_activity_fails_when_activity_not_found(client):
    # Arrange
    activity_name = "Nonexistent Club"
    email = "test@example.com"

    # Act
    response = client.delete(f"/activities/{activity_name}/participants/{email}")

    # Assert
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Activity not found"
