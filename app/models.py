import requests
from flask import current_app
from app import db, login_manager
from flask_login import UserMixin
from datetime import datetime
import random
import string


class User(UserMixin, db.Model):

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)

    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)

    # Role — either 'trainer' or 'member'
    role = db.Column(db.String(20), nullable=False)

    # Trainer info
    trainer_code = db.Column(db.String(6), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Self-referential relationship — members link to their trainer
    trainer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    trainer = db.relationship(
        'User',
        remote_side=[id],
        backref=db.backref('members', lazy='dynamic')
    )

    # Relationships to other tables
    progress = db.relationship("Progress", backref="user", cascade="all, delete-orphan")
    food_logs = db.relationship("UserFoodLog", backref="user", lazy=True)

    def generate_trainer_code(self):
        """Generate a random 8-character trainer code."""
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        self.trainer_code = code
        db.session.add(self)
        db.session.commit()


# Flask-Login user loader
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
            
class Food(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    calories = db.Column(db.Float)
    protein_g = db.Column(db.Float)
    carbs_g = db.Column(db.Float)
    fats_g = db.Column(db.Float)
    source_id = db.Column(db.String(100))
    serving_size = db.Column(db.Float)
    serving_unit = db.Column(db.String(50))
    grams_per_unit = db.Column(db.Float)

UNIT_TO_GRAMS = {
    "g": 1,
    "kg": 1000,
    "oz": 28.35,
    "lb": 453.592,
    "tsp": 4.2,
    "tbsp": 14.3,
    "cup": 240
}
from datetime import datetime
from app import db

# Make sure this is defined somewhere
UNIT_TO_GRAMS = {
    "g": 1,
    "kg": 1000,
    "oz": 28.35,
    "lb": 453.592,
    "tsp": 4.2,   # approximate
    "tbsp": 14.3,
    "cup": 240
}

class UserFoodLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    food_id = db.Column(db.Integer, db.ForeignKey("food.id"), nullable=False)
    quantity = db.Column(db.Float, nullable=False)
    unit = db.Column(db.String(20), default="g")  # <--- add this column
    log_date = db.Column(db.Date, default=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    food = db.relationship("Food")

    @property
    def scaled(self):
        unit = self.unit.lower() if self.unit else "g"

        # Try to find a food-specific measure
        measure = FoodMeasure.query.filter_by(food_id=self.food_id, measure_name=unit).first()
        if measure:
            grams_per_unit = measure.grams
        else:
            grams_per_unit = UNIT_TO_GRAMS.get(unit, 1)  # fallback to generic

        quantity_in_grams = self.quantity * grams_per_unit

        serving_grams = self.food.serving_size or 100
        if serving_grams == 0:
            serving_grams = 100

        factor = quantity_in_grams / serving_grams

        return {
            "calories": round((self.food.calories or 0) * factor, 1),
            "protein": round((self.food.protein_g or 0) * factor, 1),
            "carbs": round((self.food.carbs_g or 0) * factor, 1),
            "fats": round((self.food.fats_g or 0) * factor, 1)
        }

class Progress(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    weight = db.Column(db.Float, nullable=True)
    notes = db.Column(db.Text, nullable=True)

class FoodMeasure(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    food_id = db.Column(db.Integer, db.ForeignKey('food.id'))
    measure_name = db.Column(db.String(50))  # "cup", "tbsp", "tsp", "slice"
    grams = db.Column(db.Float)              # how many grams that measure is

    food = db.relationship("Food", backref="measures")
    
class WorkoutTemplate(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    trainer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship to TemplateExercise
    exercises = db.relationship('TemplateExercise', backref='template', cascade="all, delete-orphan")


class TemplateExercise(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    template_id = db.Column(db.Integer, db.ForeignKey('workout_template.id'), nullable=False)
    exercise_name = db.Column(db.String(100), nullable=False)
    sets = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=False)

    def fetch_details_from_api(self):
        """
        Fetch exercise info from the API Ninjas Exercises API.
        Requires: API_NINJAS_KEY in app config.
        """
        api_key = current_app.config.get('API_NINJAS_KEY')
        if not api_key:
            raise ValueError("API_NINJAS_KEY not found in app configuration.")

        url = f"https://api.api-ninjas.com/v1/exercises?name={self.exercise_name}"
        headers = {"X-Api-Key": api_key}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data:
                exercise_data = data[0]
                return {
                    "name": exercise_data.get("name"),
                    "type": exercise_data.get("type"),
                    "muscle": exercise_data.get("muscle"),
                    "equipment": exercise_data.get("equipment"),
                    "difficulty": exercise_data.get("difficulty"),
                    "instructions": exercise_data.get("instructions")
                }
            else:
                return {"error": "No exercise data found."}
        except Exception as e:
            return {"error": str(e)}

class Client(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    # 👇 Link each client to a specific trainer (User)
    trainer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # 👇 Relationship back to the trainer (assuming User is your trainer model)
    trainer = db.relationship('User', backref='clients', lazy=True)

    # 👇 Relationship to assigned workouts
    workouts = db.relationship('ClientWorkout', backref='client', cascade='all, delete-orphan')


class ClientWorkout(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, db.ForeignKey('client.id'), nullable=False)
    template_id = db.Column(db.Integer, db.ForeignKey('workout_template.id'), nullable=False)  # ✅ FIXED
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationship now works because both sides reference the same table name
    template = db.relationship('WorkoutTemplate', backref='client_assignments')
