from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from api_utils import admin_required
from model import db, Subject, Chapter, Quiz, Question, Admin
from flask_jwt_extended import get_jwt, get_jwt_identity
from api_utils import get_current_user, get_current_ist
from datetime import datetime


admin_dashboard_bp = Blueprint('admin_dashboard', __name__)

@admin_dashboard_bp.route('/dashboard/admin', methods=['GET'])
@jwt_required()
@admin_required()
def admin_dashboard():
    claims = get_jwt()
    return jsonify({"msg": f"Welcome {claims['username']}"}), 200


@admin_dashboard_bp.route('/admin/all-data', methods=['GET'])
@jwt_required()
@admin_required()
def get_all_admin_data():
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

        # Fetch all chapters
        chapters = Chapter.query.all()
        chapters_list = [
            {
                'id': chapter.id,
                'subject_id': chapter.subject_id,
                'admin_id': chapter.admin_id,
                'name': chapter.name,
                'description': chapter.description
            } for chapter in chapters
        ]

        # Fetch all quizzes
        quizzes = Quiz.query.all()
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

        # Fetch all questions
        questions = Question.query.all()
        questions_list = [
            {
                'id': question.id,
                'quiz_id': question.quiz_id,
                'admin_id': question.admin_id,
                'question_statement': question.question_statement,
                'option1': question.option1,
                'option2': question.option2,
                'option3': question.option3,
                'option4': question.option4,
                'correct_option': question.correct_option,
                'difficulty': question.difficulty
            } for question in questions
        ]

        # Combinning all data into a single response
        response_data = {
            'subjects': subjects_list,
            'chapters': chapters_list,
            'quizzes': quizzes_list,
            'questions': questions_list
        }

        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch all data: {str(e)}"}), 500
    
