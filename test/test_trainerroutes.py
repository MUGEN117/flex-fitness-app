import pytest
from unittest.mock import patch, MagicMock
from flask import Flask
from app.trainerroutes import trainerroutes


@pytest.fixture
def client():
    """Set up a Flask test client with the trainerroutes blueprint."""
    app = Flask(__name__)
    app.register_blueprint(trainerroutes)
    app.testing = True
    return app.test_client()


def test_view_user_progress_success(client):
    mock_user = MagicMock()
    mock_user.name = "John Doe"
    mock_user.progress = [
        MagicMock(date="2025-10-21", weight=180, notes="Feeling stronger"),
        MagicMock(date="2025-10-22", weight=178, notes="Lost weight")
    ]

    with patch("trainerroutes.User.query") as mock_query:
        mock_query.filter_by.return_value.first.return_value = mock_user

        response = client.get("/trainer/1/user/2/progress")
        data = response.get_json()

        assert response.status_code == 200
        assert data["user"] == "John Doe"
        assert len(data["progress"]) == 2
        assert data["progress"][0]["weight"] == 180


def test_view_user_progress_not_found(client):
    with patch("trainerroutes.User.query") as mock_query:
        mock_query.filter_by.return_value.first.return_value = None

        response = client.get("/trainer/1/user/99/progress")
        data = response.get_json()

        assert response.status_code == 404
        assert "User not found" in data["error"]


def test_delete_user_progress_success(client):
    mock_user = MagicMock()
    mock_user.id = 2

    mock_progress = MagicMock()

    with patch("trainerroutes.User.query") as mock_user_query, \
         patch("trainerroutes.Progress.query") as mock_progress_query, \
         patch("trainerroutes.db.session") as mock_db:
        
        mock_user_query.filter_by.return_value.first.return_value = mock_user
        mock_progress_query.filter_by.return_value.first.return_value = mock_progress

        response = client.delete("/trainer/1/user/2/progress/5")
        data = response.get_json()

        assert response.status_code == 200
        assert data["message"] == "Progress entry deleted"
        mock_db.delete.assert_called_once_with(mock_progress)
        mock_db.commit.assert_called_once()


def test_delete_user_progress_user_not_found(client):
    with patch("trainerroutes.User.query") as mock_query:
        mock_query.filter_by.return_value.first.return_value = None

        response = client.delete("/trainer/1/user/2/progress/5")
        data = response.get_json()

        assert response.status_code == 404
        assert "User not found" in data["error"]


def test_delete_user_progress_not_found(client):
    mock_user = MagicMock()
    mock_user.id = 2

    with patch("trainerroutes.User.query") as mock_user_query, \
         patch("trainerroutes.Progress.query") as mock_progress_query:
        
        mock_user_query.filter_by.return_value.first.return_value = mock_user
        mock_progress_query.filter_by.return_value.first.return_value = None

        response = client.delete("/trainer/1/user/2/progress/999")
        data = response.get_json()

        assert response.status_code == 404
        assert "Progress entry not found" in data["error"]