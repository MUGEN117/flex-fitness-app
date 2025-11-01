from flask import Blueprint, render_template, session, request, redirect, url_for, flash
from app import db
from app.models import User, WorkoutTemplate, TemplateExercise
from flask_login import login_required, current_user

trainer_bp = Blueprint('trainer', __name__, url_prefix="/trainer")

@trainer_bp.route('/trainer/clients')
def view_clients():
    trainer_id = session.get('user_id')  # the logged-in trainer
    if not trainer_id:
        return "Please log in first", 403

    # Only fetch members assigned to this trainer
    clients = User.query.filter_by(trainer_id=trainer_id, role='member').all()

    return render_template('display-trainer.html', clients=clients)

@trainer_bp.route('/dashboard-trainer')
@login_required
def dashboard_trainer():
    if current_user.role != 'trainer':
        return "Access denied", 403
    return render_template('dashboard-trainer.html', trainer=current_user)

# -----------------------------
# Create Workout Template
# -----------------------------
@trainer_bp.route('/create-template', methods=['GET', 'POST'])
@login_required
def create_template():
    if current_user.role != 'trainer':
        return "Access denied", 403

    if request.method == 'POST':
        name = request.form.get('name')
        exercises = request.form.getlist('exercise')
        reps = request.form.getlist('reps')
        sets = request.form.getlist('sets')

        if not name or not exercises:
            flash('Template name and at least one exercise are required.', 'danger')
            return redirect(url_for('trainer.create_template'))

        # Save the new workout template
        template = WorkoutTemplate(
            trainer_id=current_user.id,
            name=name,
            exercises=exercises,
            reps=reps,
            sets=sets
        )
        db.session.add(template)
        db.session.commit()

        flash('Workout template created successfully!', 'success')
        return redirect(url_for('trainer.assign_template'))

    # Include existing exercises to display on create_template page
    exercises = TemplateExercise.query.filter_by(trainer_id=current_user.id).all()
    return render_template('create_template.html', exercises=exercises)

# -----------------------------
# Add Exercise to a Template
# -----------------------------
@trainer_bp.route('/add_exercise/<int:template_id>', methods=['GET', 'POST'])
@login_required
def add_exercise_to_template(template_id):
    if current_user.role != 'trainer':
        return "Access denied", 403

    # Fetch the template for this trainer
    template = WorkoutTemplate.query.filter_by(id=template_id, trainer_id=current_user.id).first()

    if not template:
        flash("Template not found or not authorized.", "danger")
        return redirect(url_for('trainer.dashboard_trainer'))

    # Handle form submission
    if request.method == 'POST':
        exercise_name = request.form.get('exercise_name')
        sets = request.form.get('sets')
        reps = request.form.get('reps')

        if not exercise_name or not sets or not reps:
            flash("All fields are required.", "danger")
            return redirect(url_for('trainer.add_exercise_to_template', template_id=template.id))

        # Create a new exercise and associate it with this template
        new_exercise = TemplateExercise(
            template_id=template.id,
            exercise_name=exercise_name,
            sets=sets,
            reps=reps
        )

        db.session.add(new_exercise)
        db.session.commit()

        flash(f"Exercise '{exercise_name}' added successfully!", "success")
        return redirect(url_for('trainer.add_exercise_to_template', template_id=template.id))

    # Render the page showing current exercises in the template
    exercises = TemplateExercise.query.filter_by(template_id=template.id).all()
    return render_template('add_exercise.html', template=template, exercises=exercises)

# -----------------------------
# Assign Template to Client
# -----------------------------
@trainer_bp.route('/assign-template', methods=['GET', 'POST'])
@login_required
def assign_template():
    if current_user.role != 'trainer':
        return "Access denied", 403

    # Fetch this trainer's templates and clients
    templates = WorkoutTemplate.query.filter_by(trainer_id=current_user.id).all()
    clients = User.query.filter_by(trainer_id=current_user.id, role='member').all()

    if request.method == 'POST':
        client_id = request.form.get('client_id')
        template_id = request.form.get('template_id')

        client = User.query.get(client_id)
        template = WorkoutTemplate.query.get(template_id)

        if not client or not template:
            flash("Invalid client or template selection.", "danger")
            return redirect(url_for('trainer.assign_template'))

        # Assignment logic (can expand later)
        flash(f"Assigned template '{template.name}' to {client.first_name} {client.last_name}.", "success")
        return redirect(url_for('trainer.dashboard_trainer'))

    return render_template('assign_template.html', templates=templates, clients=clients)
