from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required
from api_utils import admin_required
from model import db, Subject, Chapter, Quiz, Question, Admin
from flask_jwt_extended import get_jwt, get_jwt_identity
from api_utils import get_current_user
from datetime import datetime

admin_dashboard_bp = Blueprint('admin_dashboard', __name__)

@admin_dashboard_bp.route('/dashboard/admin', methods=['GET'])
@jwt_required()
@admin_required()
def admin_dashboard():
    claims = get_jwt()
    return jsonify({"msg": f"Welcome {claims['username']}"}), 200

# --- Subject Routes ---
@admin_dashboard_bp.route('/subjects', methods=['GET'])
@jwt_required()
@admin_required()
def get_subjects():
    """Fetch all subjects."""
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

@admin_dashboard_bp.route('/subjects', methods=['POST'])
@jwt_required()
@admin_required()
def create_subject():
    """Create a new subject."""
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

@admin_dashboard_bp.route('/subjects/<int:subject_id>', methods=['GET'])
@jwt_required()
@admin_required()
def get_subject(subject_id):
    """Fetch a specific subject by ID."""
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

@admin_dashboard_bp.route('/subjects/<int:subject_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_subject(subject_id):
    """Update an existing subject."""
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

@admin_dashboard_bp.route('/subjects/<int:subject_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_subject(subject_id):
    """Delete a subject by ID."""
    try:
        subject = Subject.query.get_or_404(subject_id)
        db.session.delete(subject)
        db.session.commit()
        return jsonify({"msg": "Subject deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete subject: {str(e)}"}), 500

# --- Chapter Routes ---
@admin_dashboard_bp.route('/subjects/<int:subject_id>/chapters', methods=['GET'])
@jwt_required()
@admin_required()
def get_chapters(subject_id):
    """Fetch all chapters for a subject."""
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


@admin_dashboard_bp.route('/subjects/<int:subject_id>/chapters', methods=['POST'])
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

@admin_dashboard_bp.route('/chapters/<int:chapter_id>', methods=['GET'])
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

@admin_dashboard_bp.route('/chapters/<int:chapter_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_chapter(chapter_id):
    """Update an existing chapter."""
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

@admin_dashboard_bp.route('/chapters/<int:chapter_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_chapter(chapter_id):
    """Delete a chapter by ID."""
    try:
        chapter = Chapter.query.get_or_404(chapter_id)
        db.session.delete(chapter)
        db.session.commit()
        return jsonify({"msg": "Chapter deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete chapter: {str(e)}"}), 500

# --- Quiz Routes ---
@admin_dashboard_bp.route('/chapters/<int:chapter_id>/quizzes', methods=['GET'])
@jwt_required()
@admin_required()
def get_quizzes(chapter_id):
    """Fetch all quizzes for a chapter."""
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

@admin_dashboard_bp.route('/chapters/<int:chapter_id>/quizzes', methods=['POST'])
@jwt_required()
@admin_required()
def create_quiz(chapter_id):
    """Create a new quiz under a chapter."""
    try:
        data = request.get_json()
        admin = get_current_user()

        # Parse date_of_quiz from string to Python date object
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

@admin_dashboard_bp.route('/quizzes/<int:quiz_id>', methods=['GET'])
@jwt_required()
@admin_required()
def get_quiz(quiz_id):
    """Fetch a specific quiz by ID."""
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

@admin_dashboard_bp.route('/quizzes/<int:quiz_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_quiz(quiz_id):
    """Update an existing quiz."""
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        data = request.get_json()

        # Parse date_of_quiz if provided
        date_of_quiz_str = data.get('date_of_quiz')
        if date_of_quiz_str is not None:  # Only update if explicitly provided
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
    
@admin_dashboard_bp.route('/quizzes/<int:quiz_id>/toggle_visibility', methods=['PATCH'])
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


@admin_dashboard_bp.route('/quizzes/<int:quiz_id>/toggle_payment', methods=['PATCH'])
@jwt_required()
@admin_required()
def toggle_quiz_payment(quiz_id):
    """Toggle the pay_required status of a quiz."""
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
    
@admin_dashboard_bp.route('/quizzes/<int:quiz_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_quiz(quiz_id):
    """Delete a quiz by ID."""
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        db.session.delete(quiz)
        db.session.commit()
        return jsonify({"msg": "Quiz deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete quiz: {str(e)}"}), 500

# --- Question Routes ---
@admin_dashboard_bp.route('/quizzes/<int:quiz_id>/questions', methods=['GET'])
@jwt_required()
@admin_required()
def get_questions(quiz_id):
    """Fetch all questions for a quiz."""
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

@admin_dashboard_bp.route('/quizzes/<int:quiz_id>/questions', methods=['POST'])
@jwt_required()
@admin_required()
def create_question(quiz_id):
    """Create a new question under a quiz."""
    try:
        data = request.get_json()
        admin = get_current_user()
        
        # Validate required fields
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

@admin_dashboard_bp.route('/questions/<int:question_id>', methods=['GET'])
@jwt_required()
@admin_required()
def get_question(question_id):
    """Fetch a specific question by ID."""
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

@admin_dashboard_bp.route('/questions/<int:question_id>', methods=['PUT'])
@jwt_required()
@admin_required()
def update_question(question_id):
    """Update an existing question."""
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

@admin_dashboard_bp.route('/questions/<int:question_id>', methods=['DELETE'])
@jwt_required()
@admin_required()
def delete_question(question_id):
    """Delete a question by ID."""
    try:
        question = Question.query.get_or_404(question_id)
        db.session.delete(question)
        db.session.commit()
        return jsonify({"msg": "Question deleted successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to delete question: {str(e)}"}), 500
    
@admin_dashboard_bp.route('/admin/all-data', methods=['GET'])
@jwt_required()
@admin_required()
def get_all_admin_data():
    """Fetch all subjects, chapters, quizzes, and questions in one request."""
    try:
        # Fetch all subjects
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

        # Combine all data into a single response
        response_data = {
            'subjects': subjects_list,
            'chapters': chapters_list,
            'quizzes': quizzes_list,
            'questions': questions_list
        }

        return jsonify(response_data), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch all data: {str(e)}"}), 500