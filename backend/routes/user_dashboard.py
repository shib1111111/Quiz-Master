from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt
from model import db, Quiz, QuizPayment, QuizCart
from api_utils import user_required, get_current_user, get_current_ist
from datetime import datetime

user_dashboard_bp = Blueprint('user_dashboard', __name__)

@user_dashboard_bp.route('/dashboard/user', methods=['GET'])
@jwt_required()
@user_required()
def user_dashboard():
    claims = get_jwt()  
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


