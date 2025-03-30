from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func, extract
from model import db, User, Quiz, QuizAttempt, QuestionAttempt, Subject, Chapter,Question
from api_utils import user_required, get_current_ist, get_current_user
from datetime import datetime, timedelta

user_summary_bp = Blueprint('user_summary', __name__)

@user_summary_bp.route('/dashboard/user/scores', methods=['GET'])
@jwt_required()
@user_required()
def get_user_scores():
    try:
        current_user = get_current_user()
        current_month = datetime.now().month
        previous_month = (datetime.now().replace(day=1) - timedelta(days=1)).month

        # Query all quiz attempts with related data
        query = (
            db.session.query(QuizAttempt, Quiz, Chapter, Subject)
            .join(Quiz, QuizAttempt.quiz_id == Quiz.id, isouter=True)
            .join(Chapter, Quiz.chapter_id == Chapter.id, isouter=True)
            .join(Subject, Chapter.subject_id == Subject.id, isouter=True)
            .filter(QuizAttempt.user_id == current_user.id)
            .order_by(QuizAttempt.quiz_start_time.desc())
        )

        # Count total attempts per quiz
        attempt_counts = (
            db.session.query(QuizAttempt.quiz_id, db.func.count(QuizAttempt.id).label('attempt_count'))
            .filter(QuizAttempt.user_id == current_user.id)
            .group_by(QuizAttempt.quiz_id)
            .all()
        )
        attempt_count_dict = {row.quiz_id: row.attempt_count for row in attempt_counts if row.quiz_id}

        subjects = {}
        chapters = {}
        months = {'current': [], 'previous': [], 'older': []}
        
        for qa, q, c, s in query.all():
            score_percentage = (qa.total_score_earned / qa.total_score * 100) if qa.total_score > 0 else 0
            performance_tag = (
                'Outstanding' if score_percentage >= 75 else
                'Good' if score_percentage >= 50 else
                'Pass' if score_percentage >= 25 else
                'Fail'
            )

            attempt_data = {
                'attempt_id': qa.id,
                'quiz_id': qa.quiz_id,
                'subject': s.name if s else 'N/A',
                'chapter': c.name if c else 'N/A',
                'date': qa.quiz_start_time.strftime('%Y-%m-%d %H:%M:%S') if qa.quiz_start_time else 'N/A',
                'month': qa.quiz_start_time.month if qa.quiz_start_time else None,
                'score': qa.total_score_earned,
                'full_score': qa.total_score,
                'is_completed': qa.quiz_end_time is not None,
                'total_attempts': attempt_count_dict.get(qa.quiz_id, 0),
                'performance_tag': performance_tag,
                'quiz_meta_data': {
                    'total_questions_count': qa.total_questions_count,
                    'full_score': qa.total_score,
                    'total_attempted_qn': qa.total_attempted_qn,
                    'total_correct_ans': qa.total_correct_ans,
                    'total_wrong_ans': qa.total_wrong_ans,
                    'total_score_earned': qa.total_score_earned,
                    'total_marked_for_review_qn': qa.total_marked_for_review_qn,
                    'total_skipped_qn': qa.total_skipped_qn,
                    'total_deleted_answers': qa.total_deleted_ans,
                    'total_time_taken': qa.total_time_taken,
                    'total_answering_duration': (
                        (qa.quiz_end_time - qa.quiz_start_time).total_seconds() 
                        if qa.quiz_end_time and qa.quiz_start_time else None
                    ),
                    'attempt_time': qa.record_creation_timestamp.strftime('%Y-%m-%d %H:%M:%S') 
                        if qa.record_creation_timestamp else 'N/A',
                }
            }

            if s and s.name:
                subjects.setdefault(s.name, []).append(attempt_data)
            if c and c.name:
                chapters.setdefault(c.name, []).append(attempt_data)
            if qa.quiz_start_time:
                if qa.quiz_start_time.month == current_month:
                    months['current'].append(attempt_data)
                elif qa.quiz_start_time.month == previous_month:
                    months['previous'].append(attempt_data)
                else:
                    months['older'].append(attempt_data)
            else:
                months['older'].append(attempt_data)

        total_completed = len([qa for qa in query.all() if qa[0].quiz_end_time is not None])

        return jsonify({
            'subjects': subjects,
            'chapters': chapters,
            'months': months,
            'total_completed': total_completed
        }), 200

    except Exception as e:
        return jsonify({'msg': f'Error fetching scores: {str(e)}'}), 500


@user_summary_bp.route('/dashboard/user/export_quiz_attempts', methods=['POST'])
@jwt_required()
@user_required()
def trigger_quiz_attempts_export():
    try:
        current_user = get_current_user()
        current_user_id = current_user.id
        current_user = User.query.filter_by(id=current_user_id).first()
        if not current_user:
            return jsonify({'msg': 'User not found'}), 404
        from celery_tasks import export_quiz_attempts_to_csv
        task = export_quiz_attempts_to_csv.delay(current_user_id, current_user.email)
        return jsonify({
            'msg': 'Export job started. You will receive an email with the CSV once completed.',
            'task_id': task.id
        }), 202

    except Exception as e:
        return jsonify({'msg': f'Error triggering export: {str(e)}'}), 500

