from flask import Blueprint, jsonify
from app import db
from app.models import User, Progress

trainerroutes = Blueprint('trainerroutes', __name__)

@trainerroutes.route('/trainer/<int:trainer_id>/user/<int:user_id>/progress', methods=['GET'])
def view_user_progress(trainer_id, user_id):
    user = User.query.filter_by(id=user_id, trainer_id=trainer_id).first()
    if not user:
        return jsonify({"error": "User not found or does not belong to this trainer"}), 404

    progress_data = [
        {
            "date": p.date.isoformat(),
            "weight": p.weight,
            "notes": p.notes
        }
        for p in user.progress
    ]
    return jsonify({"user": user.name, "progress": progress_data})

@trainerroutes.route('/trainer/<int:trainer_id>/user/<int:user_id>/progress/<int:progress_id>', methods=['DELETE'])
def delete_user_progress(trainer_id, user_id, progress_id):
    user = User.query.filter_by(id=user_id, trainer_id=trainer_id).first()
    if not user:
        return jsonify({"error": "User not found or does not belong to this trainer"}), 404

    progress_entry = Progress.query.filter_by(id=progress_id, user_id=user.id).first()
    if not progress_entry:
        return jsonify({"error": "Progress entry not found"}), 404

    db.session.delete(progress_entry)
    db.session.commit()
    return jsonify({"message": "Progress entry deleted"})