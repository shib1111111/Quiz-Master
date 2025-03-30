from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from api_utils import admin_required
from model import db, Chapter
from api_utils import get_current_user, get_current_ist

admin_chapter_bp = Blueprint('admin_chapter', __name__)

@admin_chapter_bp.route('/subjects/<int:subject_id>/chapters', methods=['GET'])
@jwt_required()
@admin_required()
def get_chapters(subject_id):
    try:
        chapters = Chapter.query.filter_by(subject_id=subject_id).all()
        chapters_list = [
            {
                'id': chapter.id,
                'subject_id': chapter.subject_id,
                'admin_id': chapter.admin_id,
                'name': chapter.name,
                'description': chapter.description
            } for chapter in chapters
        ]
        return jsonify(chapters_list), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch chapters: {str(e)}"}), 500


@admin_chapter_bp.route('/subjects/<int:subject_id>/chapters', methods=['POST'])
@jwt_required()
@admin_required()
def create_chapter(subject_id):
    """Create a new chapter under a subject."""
    try:
        data = request.get_json()
        admin = get_current_user()
        chapter = Chapter(
            subject_id=subject_id,
            admin_id=admin.id,
            name=data.get('name'),
            description=data.get('description')
        )
        db.session.add(chapter)
        db.session.commit()
        chapter_data = {
            'id': chapter.id,
            'subject_id': chapter.subject_id,
            'admin_id': chapter.admin_id,
            'name': chapter.name,
            'description': chapter.description
        }
        return jsonify(chapter_data), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create chapter: {str(e)}"}), 500

@admin_chapter_bp.route('/chapters/<int:chapter_id>', methods=['GET'])
@jwt_required()
@admin_required()
def get_chapter(chapter_id):
    """Fetch a specific chapter by ID."""
    try:
        chapter = Chapter.query.get_or_404(chapter_id)
        chapter_data = {
            'id': chapter.id,
            'subject_id': chapter.subject_id,
            'admin_id': chapter.admin_id,
            'name': chapter.name,
            'description': chapter.description
        }
        return jsonify(chapter_data), 200
    except Exception as e:
        return jsonify({"error": f"Chapter not found: {str(e)}"}), 404

@admin_chapter_bp.route('/chapters/<int:chapter_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_chapter(chapter_id):
    try:
        chapter = Chapter.query.get_or_404(chapter_id)
        data = request.get_json()
        chapter.name = data.get('name', chapter.name)
        chapter.description = data.get('description', chapter.description)
        db.session.commit()
        chapter_data = {
            'id': chapter.id,
            'subject_id': chapter.subject_id,
            'admin_id': chapter.admin_id,
            'name': chapter.name,
            'description': chapter.description
        }
        return jsonify(chapter_data), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update chapter: {str(e)}"}), 500

@admin_chapter_bp.route('/chapters/<int:chapter_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_chapter(chapter_id):
    try:
        chapter = Chapter.query.get_or_404(chapter_id)
        db.session.delete(chapter)
        db.session.commit()
        return jsonify({"msg": "Chapter deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete chapter: {str(e)}"}), 500