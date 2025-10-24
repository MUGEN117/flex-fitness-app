import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from flask import Flask
from app import db
from app.models import User
from app.routes.trainerroutes import trainerroutes
from datetime import date

@pytest.fixture
def app():
    """Create a Flask app configured for testing."""
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)
    app.register_blueprint(trainerroutes)

    with app.app_context():
        db.create_all()
        # Seed sample data
        trainer = User(id=1, name="Trainer One", role="trainer")
        trainee = User(id=2, name="Trainee One", trainer_id=1, role="trainee")
        progress1 = Progress(id=1, user_id=2, date=date(2025, 10, 1), weight=150, notes="Initial weigh-in")
        progress2 = Progress(id=2, user_id=2, date=date(2025, 10, 8), weight=148, notes="Second week")
        db.session.add_all([trainer, trainee, progress1, progress2])
        db.session.commit()

    yield app

    # Teardown
    with app.app_context():
        db.drop_all()


@pytest.fixture
def client(app):
    """Return Flask test client."""
    return app.test_client()

# -----------------------
# ✅ Test: View Progress
# -----------------------

def test_view_user_progress_success(client):
    response = client.get("/trainer/1/user/2/progress")
    assert response.status_code == 200
    data = response.get_json()

    assert data["user"] == "Trainee One"
    assert len(data["progress"]) == 2
    assert data["progress"][0]["notes"] == "Initial weigh-in"


def test_view_user_progress_wrong_trainer(client):
    response = client.get("/trainer/99/user/2/progress")
    assert response.status_code == 404
    assert "error" in response.get_json()

# -----------------------
# ✅ Test: Delete Progress
# -----------------------

def test_delete_user_progress_success(client):
    response = client.delete("/trainer/1/user/2/progress/1")
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "Progress entry deleted"

    # Ensure only one progress remains
    response_check = client.get("/trainer/1/user/2/progress")
    progress_data = response_check.get_json()["progress"]
    assert len(progress_data) == 1


def test_delete_user_progress_not_found(client):
    response = client.delete("/trainer/1/user/2/progress/999")
    assert response.status_code == 404
    assert "error" in response.get_json()
