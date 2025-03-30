from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from api_utils import admin_required, get_current_ist, get_current_user
from model import db, Subject, Chapter, Quiz, Question, Admin, User, QuizAttempt, QuizPayment, QuizCart
from datetime import datetime
import pytz

admin_summary_bp = Blueprint('admin_summary', __name__)

# Route to get admin summary data
@admin_summary_bp.route('/dashboard/admin/summary', methods=['GET'])
@jwt_required()
@admin_required()
def get_admin_summary():
    try:
        current_user = get_current_user()

        current_admin_id = current_user.id if current_user else None        
        # 1. Overall System Stats
        total_users = User.query.count()
        total_quizzes = Quiz.query.filter_by(admin_id=current_admin_id).count()
        total_questions = Question.query.filter_by(admin_id=current_admin_id).count()
        total_subjects = Subject.query.filter_by(admin_id=current_admin_id).count()
        active_users = db.session.query(QuizAttempt.user_id).distinct().join(Quiz).filter(Quiz.admin_id == current_admin_id).count()
        
        # 2. Performance Metrics
        quiz_attempts = QuizAttempt.query.join(Quiz).filter(Quiz.admin_id == current_admin_id).all()
        performance_data = {'outstanding': 0, 'good': 0, 'pass': 0, 'fail': 0}
        for attempt in quiz_attempts:
            score = attempt.total_score_earned
            if score >= 80:  # Assuming a normalized max score
                performance_data['outstanding'] += 1
            elif score >= 60:
                performance_data['good'] += 1
            elif score >= 40:
                performance_data['pass'] += 1
            else:
                performance_data['fail'] += 1
        
        # 3. Monthly Engagement
        monthly_attempts = {}
        for attempt in quiz_attempts:
            month = attempt.quiz_start_time.month if attempt.quiz_start_time else get_current_ist().month
            monthly_attempts[month] = monthly_attempts.get(month, 0) + 1
        
        # 4. Subject Performance
        subject_performance = {}
        for attempt in quiz_attempts:
            quiz = attempt.quiz
            if quiz and quiz.chapter and quiz.chapter.subject:
                subject_name = quiz.chapter.subject.name
                if subject_name not in subject_performance:
                    subject_performance[subject_name] = {'total_score': 0, 'attempts': 0}
                subject_performance[subject_name]['total_score'] += attempt.total_score_earned
                subject_performance[subject_name]['attempts'] += 1
        
        # 5. Revenue Metrics
        payments = QuizPayment.query.join(Quiz).filter(Quiz.admin_id == current_admin_id).all()
        revenue_by_quiz = {}
        for payment in payments:
            if payment.quiz_id not in revenue_by_quiz:
                revenue_by_quiz[payment.quiz_id] = {'amount': 0, 'count': 0}
            revenue_by_quiz[payment.quiz_id]['amount'] += payment.amount_paid
            revenue_by_quiz[payment.quiz_id]['count'] += 1
        
        # 6. Quiz Popularity
        quiz_popularity = {}
        for attempt in quiz_attempts:
            quiz_id = attempt.quiz_id
            if quiz_id not in quiz_popularity:
                quiz_popularity[quiz_id] = {'attempts': 0, 'total_time': 0}
            quiz_popularity[quiz_id]['attempts'] += 1
            quiz_popularity[quiz_id]['total_time'] += attempt.total_time_taken
        
        # 7. Difficulty Analysis
        difficulty_analysis = {
            'easy': {'count': 0, 'total_score': 0, 'attempts': 0},
            'medium': {'count': 0, 'total_score': 0, 'attempts': 0},
            'hard': {'count': 0, 'total_score': 0, 'attempts': 0}
        }
        questions = Question.query.filter_by(admin_id=current_admin_id).all()
        for question in questions:
            difficulty_analysis[question.difficulty.lower()]['count'] += 1
        for attempt in quiz_attempts:
            quiz = attempt.quiz
            if quiz:
                difficulty_analysis['easy']['attempts'] += len([q for q in quiz.questions if q.difficulty.lower() == 'easy'])
                difficulty_analysis['medium']['attempts'] += len([q for q in quiz.questions if q.difficulty.lower() == 'medium'])
                difficulty_analysis['hard']['attempts'] += len([q for q in quiz.questions if q.difficulty.lower() == 'hard'])
                difficulty_analysis['easy']['total_score'] += attempt.total_score_earned if any(q.difficulty.lower() == 'easy' for q in quiz.questions) else 0
                difficulty_analysis['medium']['total_score'] += attempt.total_score_earned if any(q.difficulty.lower() == 'medium' for q in quiz.questions) else 0
                difficulty_analysis['hard']['total_score'] += attempt.total_score_earned if any(q.difficulty.lower() == 'hard' for q in quiz.questions) else 0
        
        # Prepare response
        response = {
            'system_stats': {
                'total_users': total_users,
                'total_quizzes': total_quizzes,
                'total_questions': total_questions,
                'total_subjects': total_subjects,
                'active_users': active_users
            },
            'performance': performance_data,
            'monthly_engagement': monthly_attempts,
            'subject_performance': subject_performance,
            'revenue': {
                'total': sum(payment.amount_paid for payment in payments),
                'by_quiz': revenue_by_quiz
            },
            'quiz_popularity': quiz_popularity,
            'difficulty_analysis': {
                diff: {
                    'total_questions': data['count'],
                    'total_score': data['total_score'],
                    'attempts': data['attempts']
                } for diff, data in difficulty_analysis.items()
            }
        }
        
        return jsonify(response), 200
        
    except Exception as e:
        return jsonify({'msg': f'Error fetching admin summary: {str(e)}'}), 500
    
# Route to trigger export of all users' quiz data
@admin_summary_bp.route('/dashboard/admin/export_all_users_quiz_data', methods=['POST'])
@jwt_required()
@admin_required()
def trigger_all_users_quiz_data_export():
    try:
        current_admin = get_current_user()
        if not current_admin:
            return jsonify({'msg': 'Admin not found'}), 404

        from celery_tasks import export_all_users_quiz_data_to_csv
        task = export_all_users_quiz_data_to_csv.delay(current_admin.id, current_admin.email)
        return jsonify({
            'msg': 'Export job started. You will receive an email with the CSV once completed.',
            'task_id': task.id
        }), 202

    except Exception as e:
        return jsonify({'msg': f'Error triggering export: {str(e)}'}), 500