from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, verify_jwt_in_request,get_jwt
from datetime import datetime, timedelta
import pytz
import uuid
import stripe
import os
from model import db, Quiz, QuizAttempt, QuizPayment, QuizCart
from api_utils import user_required, get_current_user, get_current_ist
import hashlib
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import func
from flask import send_file
import pandas as pd
from io import BytesIO
load_dotenv()

user_cart_bp = Blueprint('user_cart', __name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# Add quiz to cart
@user_cart_bp.route('/dashboard/user/quiz/<int:quiz_id>/add-to-cart', methods=['POST'])
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
@user_cart_bp.route('/dashboard/user/cart', methods=['GET'])
@jwt_required()
@user_required()
def get_cart():
    current_user = get_current_user()
    cart_items = QuizCart.query.filter_by(user_id=current_user.id).all()
    STRIPE_PUBLIC_KEY = current_app.config["STRIPE_PUBLIC_KEY"]
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
        'cart_count': len(cart_items),
        'stripe_public_key': STRIPE_PUBLIC_KEY  
    })


# Remove quiz from cart
@user_cart_bp.route('/dashboard/user/cart/<int:cart_id>/remove', methods=['DELETE'])
@jwt_required()
@user_required()
def remove_from_cart(cart_id):
    current_user = get_current_user()
    cart_item = QuizCart.query.filter_by(id=cart_id, user_id=current_user.id).first_or_404()
    
    db.session.delete(cart_item)
    db.session.commit()
    
    return jsonify({'msg': 'Quiz removed from cart'})

