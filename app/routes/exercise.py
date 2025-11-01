from flask import Blueprint, render_template, redirect, request, url_for, flash, current_app, session
from app import db
from app.models import WorkoutTemplate, TemplateExercise, Client, ClientWorkout
import requests

template_bp = Blueprint('template', __name__, url_prefix="/template", template_folder='../templates')

# API Ninjas credentials
API_KEY = "qzUBIRmlU2wjNGyum5mZGQ==yZsPL58CB2OSekGj"
API_URL = "https://api.api-ninjas.com/v1/exercises"


# --------------------------------------------------
# Home - View All Templates
# --------------------------------------------------
@template_bp.route('/')
def home():
    templates = WorkoutTemplate.query.all()
    return render_template('view_template.html', templates=templates)

@template_bp.route('/create', methods=['GET', 'POST'])
def create_template():
    # ✅ Check that a trainer is logged in
    if "user_id" not in session or session.get("role") != "trainer":
        flash("Please log in as a trainer first.", "warning")
        return redirect(url_for("auth.login_trainer"))

    trainer_id = session.get("user_id")

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        # ✅ Create and save the new workout template with trainer ID
        new_template = WorkoutTemplate(
            name=name,
            description=description,
            trainer_id=trainer_id
        )
        db.session.add(new_template)
        db.session.commit()

        flash('Workout template created successfully!', 'success')

        # ✅ Redirect to add_exercise page for this new template
        return redirect(url_for('template.add_exercise', template_id=new_template.id))

    # 🧠 Load all templates created by this trainer
    templates = WorkoutTemplate.query.filter_by(trainer_id=trainer_id).all()

    # ✅ Pass them into the template
    return render_template('create_template.html', templates=templates)

@template_bp.route('/add_exercise/<int:template_id>', methods=['GET', 'POST'])
def add_exercise(template_id):
    template = WorkoutTemplate.query.get_or_404(template_id)
    exercises = []

    # ✅ Load API key & base URL from config
    api_key = current_app.config.get('API_NINJAS_KEY')
    api_url = "https://api.api-ninjas.com/v1/exercises"
    print("Loaded API key:", api_key)

    if not api_key or api_key == "your-default-key-if-needed":
        flash("⚠️ API key not set. Please check your configuration.", "warning")

    # ✅ Step 1: Search for exercises via API
    if request.method == 'POST' and 'search' in request.form:
        muscle = request.form['muscle']

        try:
            response = requests.get(
                api_url,
                headers={'X-Api-Key': api_key},
                params={'muscle': muscle},
                timeout=10
            )
            response.raise_for_status()
            exercises = response.json()

            if not exercises:
                flash(f"No exercises found for muscle group '{muscle}'.", "info")

        except requests.RequestException as e:
            flash(f"Error fetching exercises: {e}", 'danger')

    # ✅ Step 2: Add exercise to template
    elif request.method == 'POST' and 'exercise_name' in request.form:
        exercise_name = request.form.get('exercise_name')
        sets = request.form.get('sets')
        reps = request.form.get('reps')

        exercise = TemplateExercise(
            template_id=template_id,
            exercise_name=exercise_name,
            sets=sets,
            reps=reps
        )

        # Optional: Fetch extra info if your model supports it
        if hasattr(exercise, "fetch_details_from_api"):
            details = exercise.fetch_details_from_api()
            if "error" not in details:
                flash(
                    f"✅ Added '{exercise_name}' — Muscle: {details.get('muscle')}, Equipment: {details.get('equipment')}",
                    "success"
                )
            else:
                flash(f"✅ Added '{exercise_name}' (no extra info available).", "warning")
        else:
            flash(f"✅ Added '{exercise_name}' to the template!", "success")

        db.session.add(exercise)
        db.session.commit()

    return render_template('add_exercise.html', template=template, exercises=exercises)

# --------------------------------------------------
# Manage Clients (Trainer can view or add clients)
# --------------------------------------------------
@template_bp.route('/clients/<int:template_id>', methods=["GET", "POST"])
def manage_clients(template_id):
    if request.method == "POST":
        name = request.form.get("name")
        email = request.form.get("email", "")
        new_client = Client(name=name, email=email)
        db.session.add(new_client)
        db.session.commit()
        return redirect(url_for("template.manage_clients", template_id=template_id))

    clients = Client.query.all()
    return render_template("clients.html", clients=clients, template_id=template_id)


# --------------------------------------------------
# Assign Template to Client
# --------------------------------------------------
@template_bp.route('/assign/<int:template_id>', methods=['GET', 'POST'])
def assign_template(template_id):
    # Ensure a trainer is logged in
    if "user_id" not in session or session.get("role") != "trainer":
        flash("Please log in as a trainer first.", "warning")
        return redirect(url_for("auth.login_trainer"))

    trainer_id = session.get("user_id")
    template = WorkoutTemplate.query.get_or_404(template_id)

    # Optional: restrict assignment only to templates owned by this trainer
    if template.trainer_id != trainer_id:
        flash("You are not authorized to assign this template.", "danger")
        return redirect(url_for("template.home"))

    # Show only this trainer's clients
    clients = Client.query.filter_by(trainer_id=trainer_id).all()

    if request.method == 'POST':
        client_id = request.form.get('client_id')

        # Prevent duplicate assignments
        existing_assignment = ClientWorkout.query.filter_by(
            client_id=client_id, template_id=template_id
        ).first()

        if existing_assignment:
            flash("This client already has this template assigned.", "warning")
            return redirect(url_for('template.assign_template', template_id=template_id))

        # Create new assignment
        new_assignment = ClientWorkout(client_id=client_id, template_id=template_id)
        db.session.add(new_assignment)
        db.session.commit()

        flash('Template successfully assigned to client!', 'success')
        return redirect(url_for('template.home'))

    return render_template('assign_template.html', template=template, clients=clients)

