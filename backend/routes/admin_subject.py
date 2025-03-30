from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from api_utils import admin_required
from model import db, Subject
from api_utils import get_current_user, get_current_ist

admin_subject_bp = Blueprint('admin_subject', __name__)

   
# Routes for getting, creating, updating, and deleting subjects
@admin_subject_bp.route('/subjects', methods=['GET'])
@jwt_required()
@admin_required()
def get_all_subjects():
    try:
        subjects = Subject.query.all()
        subjects_list = [
            {
                'id': subject.id,
                'name': subject.name,
                'description': subject.description,
                'admin_id': subject.admin_id
            } for subject in subjects
        ]
        return jsonify(subjects_list), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch subjects: {str(e)}"}), 500

@admin_subject_bp.route('/subjects', methods=['POST'])
@jwt_required()
@admin_required()
def create_subject():
    try:
        data = request.get_json()
        admin = get_current_user()
        subject = Subject(
            name=data.get('name'),
            description=data.get('description'),
            admin_id=admin.id
        )
        db.session.add(subject)
        db.session.commit()
        subject_data = {
            'id': subject.id,
            'name': subject.name,
            'description': subject.description,
            'admin_id': subject.admin_id
        }
        return jsonify(subject_data), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create subject: {str(e)}"}), 500

@admin_subject_bp.route('/subjects/<int:subject_id>', methods=['GET'])
@jwt_required()
@admin_required()
def get_subject(subject_id):
    try:
        subject = Subject.query.get_or_404(subject_id)
        subject_data = {
            'id': subject.id,
            'name': subject.name,
            'description': subject.description,
            'admin_id': subject.admin_id
        }
        return jsonify(subject_data), 200
    except Exception as e:
        return jsonify({"error": f"Subject not found: {str(e)}"}), 404

@admin_subject_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_subject(subject_id):
    try:
        subject = Subject.query.get_or_404(subject_id)
        data = request.get_json()
        subject.name = data.get('name', subject.name)
        subject.description = data.get('description', subject.description)
        db.session.commit()
        subject_data = {
            'id': subject.id,
            'name': subject.name,
            'description': subject.description,
            'admin_id': subject.admin_id
        }
        return jsonify(subject_data), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update subject: {str(e)}"}), 500

@admin_subject_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_subject(subject_id):
    try:
        subject = Subject.query.get_or_404(subject_id)
        db.session.delete(subject)
        db.session.commit()
        return jsonify({"msg": "Subject deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete subject: {str(e)}"}), 500


