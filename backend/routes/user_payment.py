from flask import Blueprint, jsonify, request, current_app
from flask_jwt_extended import jwt_required
import stripe
import os
from model import db,User, Quiz, Question, QuizAttempt, QuestionAttempt, QuizEventLog, QuizPayment, QuizCart, Chapter, Subject
from api_utils import user_required, get_current_user, get_current_ist
from dotenv import load_dotenv
from sqlalchemy import func
from flask import send_file
from io import BytesIO


load_dotenv()

user_payment_bp = Blueprint('user_payment', __name__)

stripe.api_key = os.getenv("STRIPE_SECRET_KEY")



@user_payment_bp.route('/dashboard/user/cart/purchase', methods=['POST'])
@jwt_required()
@user_required()
def initiate_checkout():
    current_user = get_current_user()
    cart_items = QuizCart.query.filter_by(user_id=current_user.id).all()
    if not cart_items:
        return jsonify({'msg': 'Cart is empty'}), 400
    
    try:
        total_amount = sum(item.quiz.pay_amount * 100 for item in cart_items)
        line_items = [{
            'price_data': {
                'currency': 'inr',
                'product_data': {
                    'name': f"Quiz #{item.quiz.id} - {item.quiz.chapter.name}",
                },
                'unit_amount': int(item.quiz.pay_amount * 100),
            },
            'quantity': 1,
        } for item in cart_items]
        
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=line_items,
            mode='payment',
            success_url=f"{current_app.config['FRONTEND_URL']}/cart/success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{current_app.config['FRONTEND_URL']}/cart",
            metadata={
                'user_id': str(current_user.id),
                'quiz_ids': ','.join(str(item.quiz_id) for item in cart_items)
            }
        )
        
        for item in cart_items:
            quiz = item.quiz
            payment = QuizPayment(
                user_id=current_user.id,
                quiz_id=quiz.id,
                amount_paid=quiz.pay_amount,
                payment_status='Pending',
                payment_method='stripe',
                transaction_id=checkout_session.id,
                created_at=get_current_ist()
            )
            db.session.add(payment)
        
        db.session.commit()
        
        return jsonify({
            'msg': 'Checkout session created',
            'session_id': checkout_session.id
        }), 200
        
    except stripe.error.StripeError as e:
        db.session.rollback()
        return jsonify({'msg': f'Payment initiation failed: {str(e)}'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Unexpected error: {str(e)}'}), 500

# Verify payment after Stripe redirect
@user_payment_bp.route('/dashboard/user/cart/verify-payment/<session_id>', methods=['GET'])
@jwt_required()
@user_required()
def verify_payment(session_id):
    current_user = get_current_user()
    
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        
        if session.metadata['user_id'] != str(current_user.id):
            return jsonify({'msg': 'Unauthorized payment verification attempt'}), 403
            
        if session.payment_status == 'paid':
            quiz_ids = session.metadata['quiz_ids'].split(',')
            for quiz_id in quiz_ids:
                payment = QuizPayment.query.filter_by(
                    user_id=current_user.id,
                    quiz_id=int(quiz_id),
                    transaction_id=session_id
                ).first()
                
                if payment:
                    payment.payment_status = 'Completed'
                    payment.updated_at = get_current_ist()
                    cart_item = QuizCart.query.filter_by(
                        user_id=current_user.id,
                        quiz_id=int(quiz_id)
                    ).first()
                    if cart_item:
                        db.session.delete(cart_item)
            
            db.session.commit()
            # Send success email asynchronously
            from celery_tasks import send_payment_status_email
            send_payment_status_email.delay(
                recipient_email=current_user.email,
                quiz_ids=quiz_ids,
                payment_status='Completed',
                transaction_id=session_id
            )
            return jsonify({'msg': 'Payment verified and processed successfully'}), 200
            
        elif session.payment_status == 'unpaid':
            QuizPayment.query.filter_by(transaction_id=session_id).update({
                'payment_status': 'Failed',
                'updated_at': get_current_ist()
            })
            db.session.commit()
            # Send failure email asynchronously
            send_payment_status_email.delay(
                recipient_email=current_user.email,
                quiz_ids=quiz_ids,
                payment_status='Failed',
                transaction_id=session_id
            )
            return jsonify({'msg': 'Payment failed'}), 400
            
        return jsonify({'msg': 'Payment still processing'}), 202
        
    except stripe.error.StripeError as e:
        db.session.rollback()
        return jsonify({'msg': f'Payment verification failed: {str(e)}'}), 500
    except Exception as e:
        db.session.rollback()
        return jsonify({'msg': f'Unexpected error: {str(e)}'}), 500

# Stripe Webhook
@user_payment_bp.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = current_app.config.get("STRIPE_WEBHOOK_SECRET", "your_stripe_webhook_secret")
    
    try:
        event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            user_id = session['metadata']['user_id']
            quiz_ids = session['metadata']['quiz_ids'].split(',')
            
            if session.payment_status == 'paid':
                for quiz_id in quiz_ids:
                    payment = QuizPayment.query.filter_by(
                        user_id=int(user_id),
                        quiz_id=int(quiz_id),
                        transaction_id=session['id']
                    ).first()
                    
                    if payment:
                        payment.payment_status = 'Completed'
                        payment.updated_at = get_current_ist()
                        cart_item = QuizCart.query.filter_by(
                            user_id=int(user_id),
                            quiz_id=int(quiz_id)
                        ).first()
                        if cart_item:
                            db.session.delete(cart_item)
            
                db.session.commit()
        
        return jsonify({'status': 'success'}), 200
        
    except ValueError:
        return jsonify({'status': 'invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        return jsonify({'status': 'invalid signature'}), 400
    except Exception as e:
        return jsonify({'status': f'error: {str(e)}'}), 500
    
