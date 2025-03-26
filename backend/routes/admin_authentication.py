# /routes/auth.py
from datetime import timedelta
from flask import Blueprint, request, jsonify,current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity,verify_jwt_in_request,decode_token,create_refresh_token
from model import db, Admin, UserActivity  # Ensure your model file defines these models and the get_current_ist function for timestamps
from setup_cache import cache  # Global cache instance
from api_utils import get_system_info  # Import our helper function
from functools import wraps
from setup_cache import cache
import random
import string

admin_auth_bp = Blueprint('admin_authentication', __name__)


@admin_auth_bp.route('/refresh', methods=['POST'])
@jwt_required(refresh=True)
def refresh():
    current_user = get_jwt_identity()
    new_token = create_access_token(identity=current_user)
    return jsonify(access_token=new_token), 200


def generate_otp(length=6):
    digits = string.digits
    return ''.join(random.choice(digits) for _ in range(length))

@admin_auth_bp.route('/login/admin', methods=['POST'])
def admin_login():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"msg": "No input data provided."}), 400

        email = data.get('email')
        password = data.get('password')
        if not email or not password:
            return jsonify({"msg": "Email and password are required."}), 400

        admin = Admin.query.filter_by(email=email).first()
        if not admin or not check_password_hash(admin.password, password):
            return jsonify({"msg": "Invalid email or password."}), 401

        identity = admin.email  # String sub
        additional_claims = {"role": "admin", "username": admin.username,'id':admin.id}
        access_token = create_access_token(identity=identity, additional_claims=additional_claims)
        refresh_token = create_refresh_token(identity=identity, additional_claims=additional_claims)
        JWT_ACCESS_TOKEN_EXPIRES = current_app.config["JWT_ACCESS_TOKEN_EXPIRES"]
        JWT_REFRESH_TOKEN_EXPIRES = current_app.config["JWT_REFRESH_TOKEN_EXPIRES"]
        cache.set(f"admin_{admin.id}_access", access_token, timeout=JWT_ACCESS_TOKEN_EXPIRES)
        cache.set(f"admin_{admin.id}_refresh", refresh_token, timeout=JWT_REFRESH_TOKEN_EXPIRES)
        try:
            system_info = get_system_info(request)
            new_activity = UserActivity(
                user_id=admin.id,
                user_role="admin",
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
            print(f"Error logging admin activity (login): {e}")
        return jsonify({"msg": "Admin login successful.", "access_token": access_token,"refresh_token":refresh_token,"role": "admin" }), 200

    except Exception as e:
        return jsonify({"msg": f"An error occurred during admin login: {str(e)}"}), 500

@admin_auth_bp.route('/logout/admin', methods=['POST'])
@jwt_required()
def admin_logout():
    print("logout")
    try:
        admin_identity = get_jwt_identity() 
        admin = Admin.query.filter_by(email=admin_identity).first()  # Use string directly
        if admin:
            cache.delete(f"admin_{admin.id}_access")
            try:
                system_info = get_system_info(request)
                new_activity = UserActivity(
                    user_id=admin.id,
                    user_role="admin",  # Hardcoded or fetch from get_jwt()['role'] if needed
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
                print(f"Error logging admin activity (logout): {e}")
        return jsonify({"msg": "Admin logged out successfully."}), 200
    except Exception as e:
        return jsonify({"msg": f"Error during logout: {str(e)}"}), 500
    
@admin_auth_bp.route('/forgot_password/admin', methods=['POST'])
def admin_forgot_password():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"msg": "Input data required."}), 400

        username = data.get('username')
        email = data.get('email')

        if not username and not email:
            return jsonify({"msg": "Please provide a username, email, or both."}), 400

        # Query for the admin using provided fields
        admin = None
        if username and email:
            admin = Admin.query.filter_by(username=username, email=email).first()
        elif username:
            admin = Admin.query.filter_by(username=username).first()
        elif email:
            admin = Admin.query.filter_by(email=email).first()

        if not admin:
            return jsonify({"msg": "Admin not found."}), 404

        # Generate a 6-digit OTP
        otp = generate_otp()

        # Store OTP in Redis with 15-minute expiration
        cache_key = f"otp:{otp}"
        cache_data = {
                    "otp": otp,
                    "user_id": admin.id,
                    "email": admin.email,
                    "username": admin.username
                }
        cache.set(cache_key, cache_data, timeout=15 * 60)  # 15 minutes in seconds
        # Log the password reset request activity
        try:
            system_info = get_system_info(request)
            new_activity = UserActivity(
                user_id=admin.id,
                user_role="admin",
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

        # If the admin has an email, send the OTP via email using Celery
        if admin.email:
            from celery_tasks import send_reset_password_email
            send_reset_password_email.delay(admin.email, otp)
            return jsonify({"msg": "OTP generated and emailed."}), 200
        # else:
        #     # For browser-based flows without email, return the OTP directly
        #     return jsonify({"msg": "OTP generated.", "otp": otp}), 200

    except Exception as e:
        return jsonify({"msg": f"Error generating OTP: {str(e)}"}), 500
    
    
@admin_auth_bp.route('/reset_password/admin', methods=['POST'])
def admin_reset_password():
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
        admin = Admin.query.get(user_id)
        if not admin:
            return jsonify({"msg": "User not found."}), 404

        # Update password
        admin.password = generate_password_hash(new_password)
        db.session.commit()

        # Clear OTP from Redis after successful use
        cache.delete(cache_key)

        # Log the password reset activity
        try:
            system_info = get_system_info(request)
            new_activity = UserActivity(
                user_id=admin.id,
                user_role="admin",
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
        if admin.email:
            from celery_tasks import send_reset_password_success_email
            send_reset_password_success_email.delay(admin.email)
            return jsonify({"msg": "Password has been reset successfully."}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"msg": f"Error during password reset: {str(e)}"}), 500