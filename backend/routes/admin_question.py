from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from api_utils import admin_required
from model import db, Question
from api_utils import get_current_user

admin_question_bp = Blueprint('admin_question', __name__)

# Routes for getting, creating, updating, and deleting questions
@admin_question_bp.route('/quizzes/<int:quiz_id>/questions', methods=['GET'])
@jwt_required()
@admin_required()
def get_questions(quiz_id):
    try:
        questions = Question.query.filter_by(quiz_id=quiz_id).all()
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
        return jsonify(questions_list), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch questions: {str(e)}"}), 500


@admin_question_bp.route('/quizzes/<int:quiz_id>/questions', methods=['POST'])
@jwt_required()
@admin_required()
def create_question(quiz_id):
    try:
        data = request.get_json()
        admin = get_current_user()
        

        required_fields = ['question_statement', 'option1', 'option2', 'option3', 'option4', 'correct_option']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing or empty required field: {field}"}), 400

        question = Question(
            quiz_id=quiz_id,
            admin_id=admin.id,
            question_statement=data.get('question_statement'),
            option1=data.get('option1'),
            option2=data.get('option2'),
            option3=data.get('option3'),
            option4=data.get('option4'),
            correct_option=data.get('correct_option'),
            difficulty=data.get('difficulty', 'easy')
        )
        db.session.add(question)
        db.session.commit()
        
        question_data = {
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
        }
        return jsonify(question_data), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to create question: {str(e)}"}), 500

@admin_question_bp.route('/questions/<int:question_id>', methods=['GET'])
@jwt_required()
@admin_required()
def get_question(question_id):
    try:
        question = Question.query.get_or_404(question_id)
        question_data = {
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
        }
        return jsonify(question_data), 200
    except Exception as e:
        return jsonify({"error": f"Question not found: {str(e)}"}), 404

@admin_question_bp.route('/questions/<int:question_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_question(question_id):
    try:
        question = Question.query.get_or_404(question_id)
        data = request.get_json()
        
        question.question_statement = data.get('question_statement', question.question_statement)
        question.option1 = data.get('option1', question.option1)
        question.option2 = data.get('option2', question.option2)
        question.option3 = data.get('option3', question.option3)
        question.option4 = data.get('option4', question.option4)
        question.correct_option = data.get('correct_option', question.correct_option)
        question.difficulty = data.get('difficulty', question.difficulty)
        
        db.session.commit()
        
        question_data = {
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
        }
        return jsonify(question_data), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to update question: {str(e)}"}), 500

@admin_question_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_question(question_id):
    try:
        question = Question.query.get_or_404(question_id)
        db.session.delete(question)
        db.session.commit()
        return jsonify({"msg": "Question deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete question: {str(e)}"}), 500
    
