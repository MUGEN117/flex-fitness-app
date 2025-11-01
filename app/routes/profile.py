from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from app import db
from app.models import User

profile_bp = Blueprint('profile', __name__, url_prefix="/profile")

@profile_bp.route('/edit', methods=['GET', 'POST'])
def edit_profile():
    user_id = session.get('user_id')
    role = session.get('role')

    if not user_id:
        flash("You must be logged in to view this page.")
        return redirect(url_for('auth.login_member'))

    user = User.query.get(user_id)
    if not user:
        flash("User not found.")
        return redirect(url_for('main.home'))

    if request.method == 'POST':
        # Allow members to edit their profile
        if role == 'member':
            user.first_name = request.form.get('first_name', user.first_name)
            user.last_name = request.form.get('last_name', user.last_name)
            user.email = request.form.get('email', user.email)
            # Optional gender field (if added to database later)
            gender = request.form.get('gender')
            if gender:
                user.gender = gender

            db.session.commit()
            flash("Profile updated successfully!")
        else:
            flash("Only members can edit their profiles.")

    return render_template('edit-profile.html', user=user, role=role)


@profile_bp.route('/view/<int:member_id>')
def view_profile(member_id):
    trainer_id = session.get('user_id')
    role = session.get('role')

    if not trainer_id or role != 'trainer':
        return "Access denied", 403

    # Trainer can only view members assigned to them
    member = User.query.filter_by(id=member_id, trainer_id=trainer_id, role='member').first()

    if not member:
        flash("Member not found or not assigned to you.")
        return redirect(url_for('trainer.view_clients'))

    return render_template('view-profile.html', member=member)