from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request,get_jwt
from datetime import datetime, timedelta
import pytz
import uuid
from model import db,User, Quiz, Question, QuizAttempt, QuestionAttempt, QuizEventLog, QuizPayment, QuizCart
from api_utils import user_required, get_current_user, get_current_ist
import hashlib
from datetime import datetime
user_dashboard_bp = Blueprint('user_dashboard', __name__)

# Helper function to get current IST time
def get_current_ist():
    return datetime.now(pytz.timezone("Asia/Kolkata"))

def validate_exam_access_token(quiz_attempt_id, access_token):
    """Validate quiz attempt access token"""
    try:
        quiz_attempt = QuizAttempt.query.get(quiz_attempt_id)
        return (quiz_attempt and 
                quiz_attempt.access_token == access_token and 
                not quiz_attempt.quiz_end_time)
    except Exception as e:
        print(f"Error validating access token: {str(e)}")
        return False

@user_dashboard_bp.route('/dashboard/user', methods=['GET'])
@jwt_required()
@user_required()
def user_dashboard():
    claims = get_jwt()  # Full claims including role, username
    return jsonify({"msg": f"Welcome {claims['username']}"}), 200


# Get all quizzes and cart info
@user_dashboard_bp.route('/dashboard/user/quizzes', methods=['GET'])
@jwt_required()
@user_required()
def get_user_quizzes():
    current_user = get_current_user()
    current_date = get_current_ist()
    
    quizzes = Quiz.query.filter_by(visibility=True).all()
    quiz_payments = {p.quiz_id: p.payment_status for p in QuizPayment.query.filter_by(user_id=current_user.id).all()}
    quiz_carts = {c.quiz_id: c.id for c in QuizCart.query.filter_by(user_id=current_user.id).all()}
    
    quiz_data = []
    for quiz in quizzes:
        data = {
            'quiz_id': quiz.id,
            'chapter': quiz.chapter.name,
            'subject': quiz.chapter.subject.name,
            'number_of_questions': len(quiz.questions),
            'date': quiz.date_of_quiz.strftime('%Y-%m-%d'),
            'duration': f"{quiz.time_duration // 60:02d}:{quiz.time_duration % 60:02d}",
            'overall_difficulty': str(quiz.overall_difficulty),
            'pay_required': quiz.pay_required,
            'pay_amount': quiz.pay_amount,
            'paid': quiz_payments.get(quiz.id) == 'Completed' if quiz.pay_required else True,
            'in_cart': quiz.id in quiz_carts
        }
        quiz_data.append(data)
    
    return jsonify({
        'quizzes': quiz_data,
        'cart_count': len(quiz_carts)
    })

# Get quiz metadata
@user_dashboard_bp.route('/dashboard/user/quiz/<int:quiz_id>/metadata', methods=['GET'])
@jwt_required()
@user_required()
def get_quiz_metadata(quiz_id):
    quiz = Quiz.query.get_or_404(quiz_id)
    if not quiz.visibility:
        return jsonify({'msg': 'Quiz not visible'}), 403
    
    metadata = {
        'quiz_id': quiz.id,
        'subject': quiz.chapter.subject.name,
        'chapter': quiz.chapter.name,
        'number_of_questions': len(quiz.questions),
        'date': quiz.date_of_quiz.strftime('%Y-%m-%d'),
        'overall_difficulty': str(quiz.overall_difficulty),
        'pay_required': quiz.pay_required,
        'pay_amount': quiz.pay_amount,
        'duration': f"{quiz.time_duration // 60:02d}:{quiz.time_duration % 60:02d}"
    }
    return jsonify({'quiz_metadata': metadata})

# Add quiz to cart
@user_dashboard_bp.route('/dashboard/user/quiz/<int:quiz_id>/add-to-cart', methods=['POST'])
@jwt_required()
@user_required()
def add_to_cart(quiz_id):
    current_user = get_current_user()
    quiz = Quiz.query.get_or_404(quiz_id)
    
    if not quiz.pay_required:
        return jsonify({'msg': 'Free quizzes cannot be added to cart'}), 400
    
    if QuizPayment.query.filter_by(user_id=current_user.id, quiz_id=quiz_id, payment_status='Completed').first():
        return jsonify({'msg': 'Quiz already purchased'}), 400
    
    if QuizCart.query.filter_by(user_id=current_user.id, quiz_id=quiz_id).first():
        return jsonify({'msg': 'Quiz already in cart'}), 400
    
    cart_item = QuizCart(user_id=current_user.id, quiz_id=quiz_id)
    db.session.add(cart_item)
    db.session.commit()
    
    return jsonify({'msg': 'Quiz added to cart', 'quiz_id': quiz_id})

# Get cart contents
@user_dashboard_bp.route('/dashboard/user/cart', methods=['GET'])
@jwt_required()
@user_required()
def get_cart():
    current_user = get_current_user()
    cart_items = QuizCart.query.filter_by(user_id=current_user.id).all()
    
    cart_data = []
    total_amount = 0
    for item in cart_items:
        quiz = item.quiz
        cart_data.append({
            'cart_id': item.id,
            'quiz_id': quiz.id,
            'subject': quiz.chapter.subject.name,
            'chapter': quiz.chapter.name,
            'date': quiz.date_of_quiz.strftime('%Y-%m-%d'),
            'pay_amount': quiz.pay_amount,
            'overall_difficulty': str(quiz.overall_difficulty)
        })
        total_amount += quiz.pay_amount
    
    return jsonify({
        'cart_items': cart_data,
        'total_amount': total_amount,
        'cart_count': len(cart_items)
    })

# Remove quiz from cart
@user_dashboard_bp.route('/dashboard/user/cart/<int:cart_id>/remove', methods=['DELETE'])
@jwt_required()
@user_required()
def remove_from_cart(cart_id):
    current_user = get_current_user()
    cart_item = QuizCart.query.filter_by(id=cart_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(cart_item)
    db.session.commit()
    
    return jsonify({'msg': 'Quiz removed from cart'})

# Purchase all items in cart
@user_dashboard_bp.route('/dashboard/user/cart/purchase', methods=['POST'])
@jwt_required()
@user_required()
def purchase_cart():
    current_user = get_current_user()
    cart_items = QuizCart.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        return jsonify({'msg': 'Cart is empty'}), 400
    
    for item in cart_items:
        quiz = item.quiz
        payment = QuizPayment(
            user_id=current_user.id,
            quiz_id=quiz.id,
            amount_paid=quiz.pay_amount,
            payment_status='Completed',  # Dummy payment
            transaction_id=f"DUMMY-{current_user.id}-{quiz.id}-{int(get_current_ist().timestamp())}"
        )
        db.session.add(payment)
        db.session.delete(item)
    
    db.session.commit()
    
    return jsonify({'msg': 'Cart purchased successfully'})

@user_dashboard_bp.route('/dashboard/user/quiz/<int:quiz_id>/open_instructions', methods=['POST'])
@jwt_required()
@user_required()
def open_instructions(quiz_id):
    """Open quiz instructions and create attempt"""
    try:
        current_user = get_current_user()
        quiz = Quiz.query.get_or_404(quiz_id)
        current_ist = get_current_ist()
        
        if quiz.date_of_quiz > current_ist.date():
            return jsonify({'msg': 'Quiz not yet available'}), 403

        access_token = hashlib.sha256(
            f"{quiz_id}-{current_user.id}-{current_ist.isoformat()}".encode()
        ).hexdigest()

        quiz_attempt = QuizAttempt(
            user_id=current_user.id,
            quiz_id=quiz_id,
            total_questions_count=len(quiz.questions),
            total_score=sum(q.score_value for q in quiz.questions),
            quiz_start_time=current_ist,
            access_token=access_token
        )
        
        db.session.add(quiz_attempt)
        db.session.flush()

        event_log = QuizEventLog(
            user_id=current_user.id,
            quiz_attempt_id=quiz_attempt.id,
            event_type='VIEW_INSTRUCTIONS',
            event_timestamp=current_ist,
            event_details=f"User {current_user.id} opened instructions for quiz {quiz_id}"
        )
        
        db.session.add(event_log)
        db.session.commit()

        return jsonify({
            'msg': 'Instructions opened successfully',
            'quiz_id': quiz_id,
            'quiz_attempt_id': quiz_attempt.id,
            'duration_minutes': quiz.time_duration,
            'access_token': quiz_attempt.access_token,
            'total_questions': quiz_attempt.total_questions_count
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error opening instructions: {str(e)}'}), 500

@user_dashboard_bp.route('/dashboard/user/quiz/<int:quiz_id>/attempt/<int:attempt_id>/start', methods=['POST'])
@jwt_required()
@user_required()
def start_exam(quiz_id, attempt_id):
    """Start exam and log the event"""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        access_token = data.get('access_token')
        
        if not access_token:
            return jsonify({'msg': 'Access token is required'}), 400

        quiz_attempt = QuizAttempt.query.get_or_404(attempt_id)
        
        if quiz_attempt.user_id != current_user.id or quiz_attempt.quiz_id != quiz_id:
            return jsonify({'msg': 'Unauthorized access'}), 403
        
        if not validate_exam_access_token(attempt_id, access_token):
            return jsonify({'msg': 'Invalid or expired access token'}), 403

        if quiz_attempt.quiz_end_time:
            return jsonify({'msg': 'Exam already completed'}), 400

        current_ist = get_current_ist()
        event_log = QuizEventLog(
            user_id=current_user.id,
            quiz_attempt_id=attempt_id,
            event_type='START_EXAM',
            event_timestamp=current_ist,
            event_details=f"User {current_user.id} started exam for quiz {quiz_id}"
        )
        
        db.session.add(event_log)
        db.session.commit()

        return jsonify({
            'msg': 'Exam started successfully',
            'quiz_id': quiz_id,
            'attempt_id': attempt_id,
            'access_token': quiz_attempt.access_token
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error starting exam: {str(e)}'}), 500

@user_dashboard_bp.route('/dashboard/user/quiz/<int:quiz_id>/questions', methods=['GET'])
@jwt_required()
@user_required()
def get_quiz_questions(quiz_id):
    """Retrieve quiz questions"""
    try:
        quiz = Quiz.query.get_or_404(quiz_id)
        questions = [{
            'id': q.id,
            'question_statement': q.question_statement,
            'options': [q.option1, q.option2, q.option3, q.option4],
            'difficulty': q.difficulty,
            'score_value': q.score_value
        } for q in quiz.questions]
        
        return jsonify(questions), 200
    
    except Exception as e:
        return jsonify({'msg': f'Error retrieving questions: {str(e)}'}), 500

@user_dashboard_bp.route('/dashboard/user/quiz/<int:quiz_id>/attempt/<int:attempt_id>/question/<int:question_id>', 
                       methods=['POST'])
@jwt_required()
@user_required()
def save_question_attempt(quiz_id, attempt_id, question_id):
    """Save user's question attempt"""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        selected_option = data.get('selected_option')
        access_token = data.get('access_token')
        
        if not selected_option:
            return jsonify({'msg': 'Selected option is required'}), 400
        if not access_token or not validate_exam_access_token(attempt_id, access_token):
            return jsonify({'msg': 'Valid access token required'}), 403

        quiz_attempt = QuizAttempt.query.get_or_404(attempt_id)
        if quiz_attempt.user_id != current_user.id or quiz_attempt.quiz_id != quiz_id:
            return jsonify({'msg': 'Unauthorized access'}), 403

        current_ist = get_current_ist()
        question_attempt = QuestionAttempt(
            quiz_attempt_id=attempt_id,
            user_id=current_user.id,
            question_id=question_id,
            selected_option=selected_option,
            question_attempt_timestamp=current_ist
        )
        
        event_log = QuizEventLog(
            user_id=current_user.id,
            quiz_attempt_id=attempt_id,
            question_id=question_id,
            event_type='SAVE_RESPONSE',
            event_timestamp=current_ist,
            event_details=f"User {current_user.id} saved response for question {question_id}"
        )
        
        db.session.add_all([question_attempt, event_log])
        db.session.commit()

        return jsonify({'msg': 'Response saved successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error saving response: {str(e)}'}), 500

@user_dashboard_bp.route('/dashboard/user/quiz/<int:quiz_id>/attempt/<int:attempt_id>/navigate/<int:question_id>', methods=['POST'])
@jwt_required()
@user_required()
def navigate_question(quiz_id, attempt_id, question_id):
    """Log question navigation"""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        access_token = data.get('access_token')
        
        if not access_token or not validate_exam_access_token(attempt_id, access_token):
            return jsonify({'msg': 'Valid access token required'}), 403

        quiz_attempt = QuizAttempt.query.get_or_404(attempt_id)
        if quiz_attempt.user_id != current_user.id or quiz_attempt.quiz_id != quiz_id:
            return jsonify({'msg': 'Unauthorized access'}), 403

        current_ist = get_current_ist()
        event_log = QuizEventLog(
            user_id=current_user.id,
            quiz_attempt_id=attempt_id,
            question_id=question_id,
            event_type='QUESTION_NUMBER_CLICK',
            event_timestamp=current_ist,
            event_details=f"User {current_user.id} navigated to question {question_id}"
        )
        
        db.session.add(event_log)
        db.session.commit()

        return jsonify({'msg': 'Navigation logged successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error logging navigation: {str(e)}'}), 500

@user_dashboard_bp.route('/dashboard/user/quiz/<int:quiz_id>/attempt/<int:attempt_id>/submit', methods=['POST'])
@jwt_required()
@user_required()
def submit_exam(quiz_id, attempt_id):
    """Submit the exam and calculate results"""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        access_token = data.get('access_token')
        
        if not access_token or not validate_exam_access_token(attempt_id, access_token):
            return jsonify({'msg': 'Valid access token required'}), 403

        quiz_attempt = QuizAttempt.query.get_or_404(attempt_id)
        if quiz_attempt.user_id != current_user.id or quiz_attempt.quiz_id != quiz_id:
            return jsonify({'msg': 'Unauthorized access'}), 403
        if quiz_attempt.quiz_end_time:
            return jsonify({'msg': 'Exam already submitted'}), 400

        current_ist = get_current_ist()
        question_attempts = QuestionAttempt.query.filter_by(quiz_attempt_id=attempt_id).all()
        
        quiz_attempt.quiz_end_time = current_ist
        current_ist = get_current_ist()
        current_ist_naive = current_ist.replace(tzinfo=None)
        quiz_attempt.total_time_taken = int(
            (current_ist_naive - quiz_attempt.quiz_start_time).total_seconds()
        )
        # quiz_attempt.total_time_taken = int(
        #     (current_ist - quiz_attempt.quiz_start_time).total_seconds()
        # )
        quiz_attempt.total_attempted_qn = len(question_attempts)
        quiz_attempt.total_correct_ans = sum(
            1 for qa in question_attempts 
            if Question.query.get(qa.question_id).correct_option == qa.selected_option
        )
        quiz_attempt.total_wrong_ans = quiz_attempt.total_attempted_qn - quiz_attempt.total_correct_ans
        quiz_attempt.total_score_earned = sum(
            Question.query.get(qa.question_id).score_value 
            if Question.query.get(qa.question_id).correct_option == qa.selected_option 
            else 0
            for qa in question_attempts
        )
        quiz_attempt.total_marked_for_review_qn = QuizEventLog.query.filter_by(
            quiz_attempt_id=attempt_id, 
            event_type='MARK_FOR_REVIEW'
        ).count()

        event_log = QuizEventLog(
            user_id=current_user.id,
            quiz_attempt_id=attempt_id,
            event_type='END_EXAMINATION',
            event_timestamp=current_ist,
            event_details=f"User {current_user.id} manually submitted quiz {quiz_id}"
        )
        
        db.session.add(event_log)
        db.session.commit()

        return jsonify({
            'msg': 'Exam submitted successfully',
            'total_score_earned': quiz_attempt.total_score_earned,
            'total_correct_ans': quiz_attempt.total_correct_ans,
            'total_time_taken': quiz_attempt.total_time_taken,
            'total_questions': quiz_attempt.total_questions_count
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error submitting exam: {str(e)}'}), 500

@user_dashboard_bp.route('/dashboard/user/quiz/<int:quiz_id>/attempt/<int:attempt_id>/end', methods=['POST'])
@jwt_required()
@user_required()
def end_exam(quiz_id, attempt_id):
    """End the exam automatically"""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        access_token = data.get('access_token')
        reason = data.get('reason', 'Unknown')
        
        if not access_token or not validate_exam_access_token(attempt_id, access_token):
            return jsonify({'msg': 'Valid access token required'}), 403

        quiz_attempt = QuizAttempt.query.get_or_404(attempt_id)
        if quiz_attempt.user_id != current_user.id or quiz_attempt.quiz_id != quiz_id:
            return jsonify({'msg': 'Unauthorized access'}), 403
        if quiz_attempt.quiz_end_time:
            return jsonify({'msg': 'Exam already ended'}), 400

        current_ist = get_current_ist()
        question_attempts = QuestionAttempt.query.filter_by(quiz_attempt_id=attempt_id).all()
        
        quiz_attempt.quiz_end_time = current_ist
        current_ist = get_current_ist()
        current_ist_naive = current_ist.replace(tzinfo=None)
        quiz_attempt.total_time_taken = int(
            (current_ist_naive - quiz_attempt.quiz_start_time).total_seconds()
        )
        # quiz_attempt.total_time_taken = int(
        #     (current_ist - quiz_attempt.quiz_start_time).total_seconds()
        # )
        quiz_attempt.total_attempted_qn = len(question_attempts)
        quiz_attempt.total_correct_ans = sum(
            1 for qa in question_attempts 
            if Question.query.get(qa.question_id).correct_option == qa.selected_option
        )
        quiz_attempt.total_wrong_ans = quiz_attempt.total_attempted_qn - quiz_attempt.total_correct_ans
        quiz_attempt.total_score_earned = sum(
            Question.query.get(qa.question_id).score_value 
            if Question.query.get(qa.question_id).correct_option == qa.selected_option 
            else 0
            for qa in question_attempts
        )
        quiz_attempt.total_marked_for_review_qn = QuizEventLog.query.filter_by(
            quiz_attempt_id=attempt_id, 
            event_type='MARK_FOR_REVIEW'
        ).count()

        event_log = QuizEventLog(
            user_id=current_user.id,
            quiz_attempt_id=attempt_id,
            event_type='END_EXAMINATION',
            event_timestamp=current_ist,
            event_details=f"User {current_user.id} exam ended for quiz {quiz_id}. Reason: {reason}"
        )
        
        db.session.add(event_log)
        db.session.commit()

        return jsonify({
            'msg': f'Exam ended due to {reason}',
            'total_score_earned': quiz_attempt.total_score_earned,
            'total_correct_ans': quiz_attempt.total_correct_ans,
            'total_time_taken': quiz_attempt.total_time_taken,
            'total_questions': quiz_attempt.total_questions_count
        }), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error ending exam: {str(e)}'}), 500

@user_dashboard_bp.route('/dashboard/user/quiz/<int:quiz_id>/attempt/<int:attempt_id>/tab-switch', methods=['POST'])
@jwt_required()
@user_required()
def log_tab_switch(quiz_id, attempt_id):
    """Log tab switch warning"""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        access_token = data.get('access_token')
        
        if not access_token or not validate_exam_access_token(attempt_id, access_token):
            return jsonify({'msg': 'Valid access token required'}), 403

        quiz_attempt = QuizAttempt.query.get_or_404(attempt_id)
        if quiz_attempt.user_id != current_user.id or quiz_attempt.quiz_id != quiz_id:
            return jsonify({'msg': 'Unauthorized access'}), 403

        current_ist = get_current_ist()
        event_log = QuizEventLog(
            user_id=current_user.id,
            quiz_attempt_id=attempt_id,
            event_type='TAB_SWITCH_WARNING',
            event_timestamp=current_ist,
            event_details=f"User {current_user.id} switched tabs during quiz {quiz_id}"
        )
        
        db.session.add(event_log)
        db.session.flush()

        warning_count = QuizEventLog.query.filter_by(
            quiz_attempt_id=attempt_id, 
            event_type='TAB_SWITCH_WARNING'
        ).count()

        if warning_count > 3:
            question_attempts = QuestionAttempt.query.filter_by(quiz_attempt_id=attempt_id).all()
            quiz_attempt.quiz_end_time = current_ist
            
            current_ist = get_current_ist()
            current_ist_naive = current_ist.replace(tzinfo=None)
            quiz_attempt.total_time_taken = int(
                (current_ist_naive - quiz_attempt.quiz_start_time).total_seconds()
            )
            quiz_attempt.total_attempted_qn = len(question_attempts)
            quiz_attempt.total_correct_ans = sum(
                1 for qa in question_attempts 
                if Question.query.get(qa.question_id).correct_option == qa.selected_option
            )
            quiz_attempt.total_wrong_ans = quiz_attempt.total_attempted_qn - quiz_attempt.total_correct_ans
            quiz_attempt.total_score_earned = sum(
                Question.query.get(qa.question_id).score_value 
                if Question.query.get(qa.question_id).correct_option == qa.selected_option 
                else 0
                for qa in question_attempts
            )
            end_event_log = QuizEventLog(
                user_id=current_user.id,
                quiz_attempt_id=attempt_id,
                event_type='END_EXAMINATION',
                event_timestamp=current_ist,
                event_details=f"User {current_user.id} exam ended due to multiple tab switches"
            )
            db.session.add(end_event_log)
            db.session.commit()
            return jsonify({'msg': 'Exam ended due to multiple tab switches'}), 403

        db.session.commit()
        return jsonify({'msg': 'Tab switch warning logged', 'warning_count': warning_count}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error logging tab switch: {str(e)}'}), 500

@user_dashboard_bp.route('/dashboard/user/quiz/<int:quiz_id>/attempt/<int:attempt_id>/mark-for-review/<int:question_id>', methods=['POST'])
@jwt_required()
@user_required()
def mark_for_review(quiz_id, attempt_id, question_id):
    """Mark question for review"""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        access_token = data.get('access_token')
        
        if not access_token or not validate_exam_access_token(attempt_id, access_token):
            return jsonify({'msg': 'Valid access token required'}), 403

        quiz_attempt = QuizAttempt.query.get_or_404(attempt_id)
        if quiz_attempt.user_id != current_user.id or quiz_attempt.quiz_id != quiz_id:
            return jsonify({'msg': 'Unauthorized access'}), 403

        current_ist = get_current_ist()
        event_log = QuizEventLog(
            user_id=current_user.id,
            quiz_attempt_id=attempt_id,
            question_id=question_id,
            event_type='MARK_FOR_REVIEW',
            event_timestamp=current_ist,
            event_details=f"User {current_user.id} marked question {question_id} for review"
        )
        
        db.session.add(event_log)
        db.session.commit()

        return jsonify({'msg': 'Question marked for review successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error marking for review: {str(e)}'}), 500

@user_dashboard_bp.route('/dashboard/user/quiz/<int:quiz_id>/attempt/<int:attempt_id>/clear-response/<int:question_id>', methods=['POST'])
@jwt_required()
@user_required()
def clear_response(quiz_id, attempt_id, question_id):
    """Clear question response"""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        access_token = data.get('access_token')
        
        if not access_token or not validate_exam_access_token(attempt_id, access_token):
            return jsonify({'msg': 'Valid access token required'}), 403

        quiz_attempt = QuizAttempt.query.get_or_404(attempt_id)
        if quiz_attempt.user_id != current_user.id or quiz_attempt.quiz_id != quiz_id:
            return jsonify({'msg': 'Unauthorized access'}), 403

        question_attempt = QuestionAttempt.query.filter_by(
            quiz_attempt_id=attempt_id, 
            question_id=question_id
        ).first()
        
        if question_attempt:
            db.session.delete(question_attempt)
            db.session.flush()

        current_ist = get_current_ist()
        event_log = QuizEventLog(
            user_id=current_user.id,
            quiz_attempt_id=attempt_id,
            question_id=question_id,
            event_type='CLEAR_RESPONSE',
            event_timestamp=current_ist,
            event_details=f"User {current_user.id} cleared response for question {question_id}"
        )
        
        db.session.add(event_log)
        db.session.commit()

        return jsonify({'msg': 'Response cleared successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error clearing response: {str(e)}'}), 500

@user_dashboard_bp.route('/dashboard/user/quiz/<int:quiz_id>/attempt/<int:attempt_id>/delete-answer/<int:question_id>', methods=['POST'])
@jwt_required()
@user_required()
def delete_answer(quiz_id, attempt_id, question_id):
    """Delete question answer"""
    try:
        current_user = get_current_user()
        data = request.get_json() or {}
        access_token = data.get('access_token')
        
        if not access_token or not validate_exam_access_token(attempt_id, access_token):
            return jsonify({'msg': 'Valid access token required'}), 403

        quiz_attempt = QuizAttempt.query.get_or_404(attempt_id)
        if quiz_attempt.user_id != current_user.id or quiz_attempt.quiz_id != quiz_id:
            return jsonify({'msg': 'Unauthorized access'}), 403

        question_attempt = QuestionAttempt.query.filter_by(
            quiz_attempt_id=attempt_id, 
            question_id=question_id
        ).first()
        
        if question_attempt:
            db.session.delete(question_attempt)
            db.session.flush()

        current_ist = get_current_ist()
        event_log = QuizEventLog(
            user_id=current_user.id,
            quiz_attempt_id=attempt_id,
            question_id=question_id,
            event_type='DELETE_ANSWER',
            event_timestamp=current_ist,
            event_details=f"User {current_user.id} deleted answer for question {question_id}"
        )
        
        db.session.add(event_log)
        db.session.commit()

        return jsonify({'msg': 'Answer deleted successfully'}), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Error deleting answer: {str(e)}'}), 500