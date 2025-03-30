# /routes/auth.py
from datetime import timedelta
from flask import Blueprint, request, jsonify,current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity,verify_jwt_in_request,decode_token,create_refresh_token
from model import db, User, Admin, UserActivity 
from setup_cache import cache  
from api_utils import get_system_info  
from functools import wraps
from setup_cache import cache
import random
import string

user_auth_bp = Blueprint('user_authentication', __name__)


@user_auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_token), 200

@user_auth_bp.route('/signup/user', methods=['POST'])
def user_signup():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"msg": "No input data provided."}), 400

        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name')
        dob = data.get('dob')
        qualification = data.get('qualification')

        if not all([username, email, password, full_name,dob,qualification]):
            return jsonify({"msg": "Please provide username, email, password,full_name,date of birth and qualification details."}), 400

        if User.query.filter_by(username=username).first():
            return jsonify({"msg": "User already exists with this username.Try another Username"}), 400

        if User.query.filter_by(email=email).first():
            return jsonify({"msg": "User already exists with this email.Try another Email Address"}), 400
        
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            full_name=full_name,
            dob=dob,
            qualification=qualification
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"msg": "User created successfully."}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error during signup: {str(e)}"}), 500

@user_auth_bp.route('/login/user', methods=['POST'])
def user_login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"msg": "No input data provided."}), 400

        email = data.get('email')
        password = data.get('password')
        # print(email, password)
        if not email or not password:
            return jsonify({"msg": "Email and password are required."}), 400

        user = User.query.filter_by(email=email).first()
        # print(user)
        if not user or not check_password_hash(user.password, password):
            return jsonify({"msg": "Invalid email or password."}), 401

        identity = user.email  
        additional_claims = {"role": "user", "username": user.username,'id':user.id}
        access_token = create_access_token(identity=identity, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=identity, additional_claims=additional_claims)
        JWT_ACCESS_TOKEN_EXPIRES = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        JWT_REFRESH_TOKEN_EXPIRES = current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]
        cache.set(f"user_{user.id}_access", access_token, timeout=JWT_ACCESS_TOKEN_EXPIRES)
        cache.set(f"user_{user.id}_refresh", refresh_token, timeout=JWT_REFRESH_TOKEN_EXPIRES)
        
        # Log user login activity
        try:
            system_info = get_system_info(request)
            new_activity = UserActivity(
                user_id=user.id,
                user_role="user",
                activity_type="login",
                client_ip=system_info.get("client_ip", "Unknown"),
                mac_address=",".join(system_info.get("mac_addresses", [])),
                os_info=system_info.get("os_info", "Unknown"),
                browser=system_info.get("browser", "Unknown"),
                device=system_info.get("device", "Unknown"),
                user_agent=system_info.get("user_agent", "Unknown"),
                memory_gb=system_info.get("memory_gb", 0),
                cpu_cores=system_info.get("cpu_cores", 0)
            )
            db.session.add(new_activity)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error logging user activity (login): {e}")

        return jsonify({"msg": "Login successful.", "access_token": access_token,"refresh_token":refresh_token, "role": "user" }), 200

    except Exception as e:
        return jsonify({"msg": f"An error occurred during login: {str(e)}"}), 500

@user_auth_bp.route('/logout/user', methods=['POST'])
@jwt_required()
def user_logout():
    try:
        user_identity = get_jwt_identity()  # Now a string (email)
        print("User identity (sub):", user_identity)
        user = User.query.filter_by(email=user_identity).first()
        if user:
            cache.delete(f"user_{user.id}_access")
            # Log user logout activity
            try:
                system_info = get_system_info(request)
                new_activity = UserActivity(
                    user_id=user.id,
                    user_role="user",
                    activity_type="logout",
                    client_ip=system_info.get("client_ip", "Unknown"),
                    mac_address=",".join(system_info.get("mac_addresses", [])),
                    os_info=system_info.get("os_info", "Unknown"),
                    browser=system_info.get("browser", "Unknown"),
                    device=system_info.get("device", "Unknown"),
                    user_agent=system_info.get("user_agent", "Unknown"),
                    memory_gb=system_info.get("memory_gb", 0),
                    cpu_cores=system_info.get("cpu_cores", 0)
                )
                db.session.add(new_activity)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"Error logging user activity (logout): {e}")
        return jsonify({"msg": "User logged out successfully."}), 200
    except Exception as e:
        return jsonify({"msg": f"Error during logout: {str(e)}"}), 500


def generate_otp(length=6):
    digits = string.digits
    return ''.join(random.choice(digits) for _ in range(length))

@user_auth_bp.route('/forgot_password/user', methods=['POST'])
def user_forgot_password_user():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"msg": "Input data required."}), 400

        username = data.get('username')
        email = data.get('email')

        if not username and not email:
            return jsonify({"msg": "Please provide a username, email, or both."}), 400

        # Query for the user using provided fields
        user = None
        if username and email:
            user = User.query.filter_by(username=username, email=email).first()
        elif username:
            user = User.query.filter_by(username=username).first()
        elif email:
            user = User.query.filter_by(email=email).first()

        if not user:
            return jsonify({"msg": "User not found."}), 404

        # Generate a 6-digit OTP
        otp = generate_otp()

        # Store OTP and user info in Redis with 15-minute expiration
        cache_key = f"otp:{otp}"
        cache_data = {
            "otp": otp,
            "user_id": user.id,
            "email": user.email,
            "username": user.username
        }
        cache.set(cache_key, cache_data, timeout=15 * 60)
        # Log the password reset request activity
        try:
            system_info = get_system_info(request)
            new_activity = UserActivity(
                user_id=user.id,
                user_role="user",
                activity_type="forgot_password",
                client_ip=system_info.get("client_ip", "Unknown"),
                mac_address=",".join(system_info.get("mac_addresses", [])),
                os_info=system_info.get("os_info", "Unknown"),
                browser=system_info.get("browser", "Unknown"),
                device=system_info.get("device", "Unknown"),
                user_agent=system_info.get("user_agent", "Unknown"),
                memory_gb=system_info.get("memory_gb", 0),
                cpu_cores=system_info.get("cpu_cores", 0)
            )
            db.session.add(new_activity)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error logging password recovery activity: {e}")

        # If the user has an email, send the OTP via email using Celery
        if user.email:
            from celery_tasks import send_reset_password_email
            send_reset_password_email.delay(user.email, otp)
        return jsonify({"msg": "OTP generated and emailed."}), 200
        # else:
        #     # For browser-based flows without email, return the OTP directly
        #     return jsonify({"msg": "OTP generated.", "otp": otp}), 200
    except Exception as e:
        return jsonify({"msg": f"Error generating OTP: {str(e)}"}), 500

@user_auth_bp.route('/reset_password/user', methods=['POST'])
def user_reset_password_user():
    try:
        data = request.get_json()
        otp = data.get('otp')
        new_password = data.get('new_password')

        if not otp or not new_password:
            return jsonify({"msg": "OTP and new password are required."}), 400

        cache_key = f"otp:{otp}"
        stored_data = cache.get(cache_key)

        if not stored_data:
            return jsonify({"msg": "Invalid or expired OTP."}), 400

        user_id = stored_data.get("user_id")
        user = User.query.get(user_id)
        if not user:
            return jsonify({"msg": "User not found."}), 404

        # Update password
        user.password = generate_password_hash(new_password)
        db.session.commit()

        # Clear OTP from Redis after successful use
        cache.delete(cache_key)

        # Log the password reset activity
        try:
            system_info = get_system_info(request)
            new_activity = UserActivity(
                user_id=user.id,
                user_role="user",
                activity_type="reset_password",
                client_ip=system_info.get("client_ip", "Unknown"),
                mac_address=",".join(system_info.get("mac_addresses", [])),
                os_info=system_info.get("os_info", "Unknown"),
                browser=system_info.get("browser", "Unknown"),
                device=system_info.get("device", "Unknown"),
                user_agent=system_info.get("user_agent", "Unknown"),
                memory_gb=system_info.get("memory_gb", 0),  
                cpu_cores=system_info.get("cpu_cores", 0)
            )
            db.session.add(new_activity)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error logging password reset activity: {e}")
         
        if user.email:   
            from celery_tasks import send_reset_password_success_email
            send_reset_password_success_email.delay(user.email)
            return jsonify({"msg": "Password has been reset successfully."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error during password reset: {str(e)}"}), 500
   