from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from api_utils import admin_required
from model import db, Subject, Chapter, Quiz, Question
from api_utils import get_current_user
from datetime import datetime

admin_quiz_bp = Blueprint('admin_quiz', __name__)

@admin_quiz_bp.route('/chapters/<int:chapter_id>/quizzes', methods=['GET'])
@jwt_required()
@admin_required()
def get_quizzes(chapter_id):
    try:
        quizzes = Quiz.query.filter_by(chapter_id=chapter_id).all()
        quizzes_list = [
            {
                'id': quiz.id,
                'chapter_id': quiz.chapter_id,
                'admin_id': quiz.admin_id,
                'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
                'time_duration': quiz.time_duration,
                'overall_difficulty': quiz.overall_difficulty,
                'visibility': quiz.visibility,
                'pay_required': quiz.pay_required,
                'pay_amount': quiz.pay_amount
            } for quiz in quizzes
        ]
        return jsonify(quizzes_list), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch quizzes: {str(e)}"}), 500

@admin_quiz_bp.route('/chapters/<int:chapter_id>/quizzes', methods=['POST'])
@jwt_required()
@admin_required()
def create_quiz(chapter_id):
    try:
        data = request.get_json()
        admin = get_current_user()

        date_of_quiz_str = data.get('date_of_quiz')
        date_of_quiz = None
        if date_of_quiz_str:
            try:
                date_of_quiz = datetime.strptime(date_of_quiz_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Invalid date format for date_of_quiz. Use YYYY-MM-DD."}), 400

        quiz = Quiz(
            chapter_id=chapter_id,
            admin_id=admin.id,
            date_of_quiz=date_of_quiz,
            time_duration=data.get('time_duration'),
            overall_difficulty=data.get('overall_difficulty'),
            visibility=data.get('visibility'),
            pay_required=data.get('pay_required', False),
            pay_amount=data.get('pay_amount', 0.0)
        )
        db.session.add(quiz)
        db.session.commit()

        quiz_data = {
            'id': quiz.id,
            'chapter_id': quiz.chapter_id,
            'admin_id': quiz.admin_id,
            'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
            'time_duration': quiz.time_duration,
            'overall_difficulty': quiz.overall_difficulty,
            'visibility': quiz.visibility,
            'pay_required': quiz.pay_required,
            'pay_amount': quiz.pay_amount
        }
        return jsonify(quiz_data), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create quiz: {str(e)}"}), 500

@admin_quiz_bp.route('/quizzes/<int:quiz_id>', methods=['GET'])
@jwt_required()
@admin_required()
def get_quiz(quiz_id):
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        quiz_data = {
            'id': quiz.id,
            'chapter_id': quiz.chapter_id,
            'admin_id': quiz.admin_id,
            'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
            'time_duration': quiz.time_duration,
            'overall_difficulty': quiz.overall_difficulty,
            'visibility': quiz.visibility,
            'pay_required': quiz.pay_required,
            'pay_amount': quiz.pay_amount
        }
        return jsonify(quiz_data), 200
    except Exception as e:
        return jsonify({"error": f"Quiz not found: {str(e)}"}), 404

@admin_quiz_bp.route('/quizzes/<int:quiz_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_quiz(quiz_id):
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        data = request.get_json()

        # Parse date_of_quiz if provided
        date_of_quiz_str = data.get('date_of_quiz')
        if date_of_quiz_str is not None:  # Only updating if explicitly provided
            try:
                quiz.date_of_quiz = datetime.strptime(date_of_quiz_str, '%Y-%m-%d').date()
            except ValueError:
                return jsonify({"error": "Invalid date format for date_of_quiz. Use YYYY-MM-DD."}), 400
            
        if 'time_duration' in data:
            quiz.time_duration = data['time_duration']

        if 'overall_difficulty' in data:
            quiz.overall_difficulty = data['overall_difficulty']

        if 'visibility' in data:
            quiz.visibility = data['visibility']
        if 'pay_required' in data:
            quiz.pay_required = data['pay_required']
        if 'pay_amount' in data:
            quiz.pay_amount = float(data['pay_amount']) if data['pay_amount'] else 0.0
        db.session.commit()
        
        quiz_data = {
            'id': quiz.id,
            'chapter_id': quiz.chapter_id,
            'admin_id': quiz.admin_id,
            'date_of_quiz': quiz.date_of_quiz.isoformat() if quiz.date_of_quiz else None,
            'time_duration': quiz.time_duration,
            'overall_difficulty': quiz.overall_difficulty,
            'visibility': quiz.visibility,
            'pay_required': quiz.pay_required,
            'pay_amount': quiz.pay_amount
        }
        return jsonify(quiz_data), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update quiz: {str(e)}"}), 500
    
@admin_quiz_bp.route('/quizzes/<int:quiz_id>/toggle_visibility', methods=['PATCH'])
@jwt_required()
@admin_required()
def toggle_quiz_visibility(quiz_id):
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        quiz.visibility = not quiz.visibility  # Toggle
        db.session.commit()
        return jsonify({"message": "Quiz visibility updated.", "visibility": quiz.visibility}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to toggle visibility: {str(e)}"}), 500


@admin_quiz_bp.route('/quizzes/<int:quiz_id>/toggle_payment', methods=['PATCH'])
@jwt_required()
@admin_required()
def toggle_quiz_payment(quiz_id):
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        quiz.pay_required = not quiz.pay_required
        if not quiz.pay_required:
            quiz.pay_amount = 0.0  # Reset amount if making it free
        db.session.commit()
        return jsonify({"message": "Quiz payment status updated.", "pay_required": quiz.pay_required, "pay_amount": quiz.pay_amount}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to toggle payment status: {str(e)}"}), 500
    
@admin_quiz_bp.route('/quizzes/<int:quiz_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_quiz(quiz_id):
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        db.session.delete(quiz)
        db.session.commit()
        return jsonify({"msg": "Quiz deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete quiz: {str(e)}"}), 500

