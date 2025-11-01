import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
from flask import template_rendered
from app.routes.exercisetemp import template_bp
from app.routes.member import member_bp


# --------------------------------------------------------
# Fixtures
# --------------------------------------------------------
@pytest.fixture
def app():
    """Create a minimal Flask app with the blueprint registered."""
    from flask import Flask
    app = Flask(__name__)
    app.secret_key = "test_secret"
    app.register_blueprint(template_bp)
    app.register_blueprint(member_bp)

    return app


@pytest.fixture
def client(app):
    """Provide a test client."""
    return app.test_client()


@pytest.fixture
def captured_templates(app):
    """Capture rendered templates and their context for assertions."""
    recorded = []

    def record(sender, template, context, **extra):
        recorded.append((template, context))

    template_rendered.connect(record, app)
    try:
        yield recorded
    finally:
        template_rendered.disconnect(record, app)


# --------------------------------------------------------
# Home route
# --------------------------------------------------------
@patch("app.routes.exercisetemp.WorkoutTemplate")
def test_home_route(mock_workout_template, client, captured_templates):
    mock_workout_template.query.all.return_value = ["template1", "template2"]

    response = client.get("/template/")
    assert response.status_code == 200

    template, context = captured_templates[0]
    assert template.name == "view_template.html"
    assert "templates" in context
    assert len(context["templates"]) == 2


# --------------------------------------------------------
# Create template (GET + POST)
# --------------------------------------------------------
@patch("app.routes.exercisetemp.db")
@patch("app.routes.exercisetemp.WorkoutTemplate")
def test_create_template_post(mock_workout_template, mock_db, client):
    mock_template_instance = MagicMock(id=1)
    mock_workout_template.return_value = mock_template_instance

    data = {
        "trainer_id": "1",
        "name": "Upper Body",
        "description": "Chest and arms day"
    }

    response = client.post("/template/create", data=data, follow_redirects=False)

    mock_db.session.add.assert_called_once()
    mock_db.session.commit.assert_called_once()
    assert response.status_code == 302  # redirect


def test_create_template_get(client, captured_templates):
    response = client.get("/template/create")
    assert response.status_code == 200
    template, _ = captured_templates[0]
    assert template.name == "create_template.html"


# --------------------------------------------------------
# Add exercise route - search API
# --------------------------------------------------------
@patch("app.routes.exercisetemp.requests.get")
@patch("app.routes.exercisetemp.WorkoutTemplate")
def test_add_exercise_search(mock_workout_template, mock_requests, client, captured_templates):
    mock_workout_template.query.get_or_404.return_value = MagicMock(id=1)
    mock_requests.return_value.status_code = 200
    mock_requests.return_value.json.return_value = [{"name": "push-up"}]

    data = {"muscle": "chest", "search": "Search"}
    response = client.post("/template/add_exercise/1", data=data)

    assert response.status_code == 200
    template, context = captured_templates[0]
    assert "exercises" in context
    assert context["exercises"][0]["name"] == "push-up"


# --------------------------------------------------------
# Add exercise route - add exercise to template
# --------------------------------------------------------
@patch("app.routes.exercisetemp.db")
@patch("app.routes.exercisetemp.TemplateExercise")
@patch("app.routes.exercisetemp.WorkoutTemplate")
def test_add_exercise_add(mock_workout_template, mock_exercise, mock_db, client):
    mock_workout_template.query.get_or_404.return_value = MagicMock(id=1)

    data = {
        "exercise_name": "Squat",
        "sets": "3",
        "reps": "10"
    }

    response = client.post("/template/add_exercise/1", data=data)
    mock_db.session.add.assert_called_once()
    mock_db.session.commit.assert_called_once()
    assert response.status_code == 200


# --------------------------------------------------------
# Manage clients (GET + POST)
# --------------------------------------------------------
@patch("app.routes.exercisetemp.Client")
@patch("app.routes.exercisetemp.db")
def test_manage_clients_post(mock_db, mock_client_model, client):
    mock_instance = MagicMock()
    mock_client_model.return_value = mock_instance

    data = {"name": "John Doe"}
    response = client.post("/template/clients/1", data=data, follow_redirects=False)

    mock_db.session.add.assert_called_once_with(mock_instance)
    mock_db.session.commit.assert_called_once()
    assert response.status_code == 302  # redirect after POST


@patch("app.routes.exercisetemp.Client")
def test_manage_clients_get(mock_client_model, client, captured_templates):
    mock_client_model.query.all.return_value = ["client1"]

    response = client.get("/template/clients/1")
    assert response.status_code == 200

    template, context = captured_templates[0]
    assert template.name == "clients.html"
    assert "clients" in context
    assert len(context["clients"]) == 1


# --------------------------------------------------------
# Assign template to client
# --------------------------------------------------------
@patch("app.routes.exercisetemp.db")
@patch("app.routes.exercisetemp.ClientWorkout")
@patch("app.routes.exercisetemp.Client")
@patch("app.routes.exercisetemp.WorkoutTemplate")
def test_assign_template_post(mock_template, mock_client, mock_clientworkout, mock_db, client):
    mock_template.query.get_or_404.return_value = MagicMock(id=1)
    mock_client.query.all.return_value = ["client1"]

    data = {"client_id": "1"}
    response = client.post("/template/assign/1", data=data, follow_redirects=False)

    mock_db.session.add.assert_called_once()
    mock_db.session.commit.assert_called_once()
    assert response.status_code == 302


@patch("app.routes.exercisetemp.Client")
@patch("app.routes.exercisetemp.WorkoutTemplate")
def test_assign_template_get(mock_template, mock_client, client, captured_templates):
    mock_template.query.get_or_404.return_value = MagicMock(id=1)
    mock_client.query.all.return_value = ["client1"]

    response = client.get("/template/assign/1")
    assert response.status_code == 200
    template, context = captured_templates[0]
    assert template.name == "assign_template.html"
    assert "clients" in context
