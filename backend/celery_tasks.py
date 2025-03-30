# /celery_tasks.py
from celery_worker import celery_app
from flask_mail import Message
from app import mail
from google_chat_utills import send_group_msg_google_chat_space
from datetime import datetime, timedelta
import pytz
from flask import render_template
from model import User, Quiz, QuizAttempt, UserActivity
from config import Config
from celery.schedules import crontab
from celery_tasks_utils import process_daily_reminder_data, get_previous_month_range, get_user_activity, process_user_data, generate_quiz_attempts_csv,generate_all_users_quiz_data_csv
import csv
from dotenv import load_dotenv
import os
from api_utils import get_current_ist

load_dotenv()
# Load the API key from the .env file
SENDER_MAIL = str(os.getenv("SENDER_MAIL"))
IST = pytz.timezone("Asia/Kolkata")
# Triggered Tasks
@celery_app.task(name="send_reset_password_email")
def send_reset_password_email(recipient_email, one_time_password="default_otp"):
    
    html_content = render_template("reset_password_request.html", one_time_password=one_time_password)
    
    # Create email message
    email_message = Message(
        subject="Password Reset Request",
        sender=SENDER_MAIL,  # Update with your sender email
        recipients=[recipient_email],
        html=html_content  # Set the HTML content
    )
    
    # Send the email
    mail.send(email_message)
    print(f"Password reset email sent to {recipient_email}")
    
@celery_app.task(name="send_reset_password_success_email")
def send_reset_password_success_email(recipient_email):
    
    html_content = render_template("reset_password_success.html")
    
    # Create email message
    email_message = Message(
        subject="Password Reset Successful",
        sender=SENDER_MAIL,  
        recipients=[recipient_email],
        html=html_content  
    )
    
    # Send the email
    mail.send(email_message)
    print(f"Password reset success email sent to {recipient_email}")
    
@celery_app.task(name="send_payment_status_email")
def send_payment_status_email(recipient_email, quiz_ids, payment_status, transaction_id):
    html_content = render_template(
        "payment_status.html",
        quiz_ids=quiz_ids,
        payment_status=payment_status,
        transaction_id=transaction_id,
        current_date=get_current_ist().strftime("%Y-%m-%d %H:%M:%S"),
    )
    
    email_message = Message(
        subject=f"Payment Status Update - {payment_status}",
        sender=SENDER_MAIL,
        recipients=[recipient_email],
        html=html_content
    )
    
    mail.send(email_message)
    print(f"Payment status email sent to {recipient_email} for transaction {transaction_id}")
    
@celery_app.task(name="send_exam_status_email")
def send_exam_status_email(recipient_email, quiz_id, attempt_id, status, score_details):
    html_content = render_template(
        "exam_status.html",
        quiz_id=quiz_id,
        attempt_id=attempt_id,
        status=status,
        score_details=score_details,
        current_date=get_current_ist().strftime("%Y-%m-%d %H:%M:%S"),
    )
    
    # Create email message
    email_message = Message(
        subject=f"Quiz #{quiz_id} - Examination {status}",
        sender=SENDER_MAIL,
        recipients=[recipient_email],
        html=html_content
    )
    
    # Send the email
    mail.send(email_message)
    print(f"Exam status email sent to {recipient_email} for quiz {quiz_id}, attempt {attempt_id}")    
    
# Daily Reminder for Users
@celery_app.task(name="send_daily_reminder")
def send_daily_reminder():
    print("Sending daily reminders...")
    try:
        (new_free_quizzes_data, new_paid_quizzes_data, endorse_free_quizzes_data, 
         endorse_paid_quizzes_data, inactive_threshold) = process_daily_reminder_data()
        
        if all(x is None for x in [new_free_quizzes_data, new_paid_quizzes_data, 
                                   endorse_free_quizzes_data, endorse_paid_quizzes_data]):
            print("No quiz data processed; skipping email sending.")
            return
        
        users = User.query.all()
        for user in users:
            try:
                last_activity = UserActivity.query.filter_by(user_id=user.id).order_by(
                    UserActivity.record_creation_timestamp.desc()
                ).first()

                should_send = False
                context = {
                    "full_name": user.full_name,
                    "new_free_quizzes": new_free_quizzes_data,
                    "new_paid_quizzes": new_paid_quizzes_data,
                    "endorse_free_quizzes": endorse_free_quizzes_data,
                    "endorse_paid_quizzes": endorse_paid_quizzes_data,
                    "inactive": False
                }

                # Check if user is inactive
                if last_activity and last_activity.record_creation_timestamp < inactive_threshold:
                    context["inactive"] = True
                    should_send = True

                # Send email if there are new or endorsement quizzes
                if (new_free_quizzes_data or new_paid_quizzes_data or 
                    endorse_free_quizzes_data or endorse_paid_quizzes_data):
                    should_send = True

                if should_send:
                    html_content = render_template("daily_reminder.html", **context)
                    email_message = Message(
                        subject="Your Daily Quiz Master Update!",
                        sender="shibkumar1002@gmail.com",  # Replace with your sender email
                        recipients=[user.email],
                        html=html_content
                    )
                    mail.send(email_message)
                    print(f"Reminder sent to {user.email}")
            except Exception as e:
                print(f"Error sending reminder to {user.email}: {e}")
    except Exception as e:
        print(f"Error in send_daily_reminder task: {e}")
          
# Monthly Report for Users
@celery_app.task(name="send_monthly_report")
def send_monthly_report():    
    # Real implementation
    start_date, end_date = get_previous_month_range()
    
    # Bypassing for testing purposes
    get_current_month_range = lambda: (
    (now := datetime.now(pytz.timezone("Asia/Kolkata"))).replace(day=1, hour=0, minute=0, second=0, microsecond=0),
    (now.replace(month=now.month % 12 + 1, day=1) if now.month != 12 else now.replace(year=now.year + 1, month=1, day=1)) - timedelta(days=1))
    start_date, end_date = get_current_month_range()
    # above line is for testing only, remove it in production
    
    print(f"Monthly report range: {start_date} to {end_date}")
    
    users = User.query.all()
    print(f"Total users: {len(users)}")
    for user in users:
        try:
            attempts, purchases = get_user_activity(user, start_date, end_date)
            print(f"User: {user.full_name}, Attempts: {len(attempts)}, Purchases: {len(purchases)}")
            if not attempts and not purchases:
                html_content = render_template("monthly_report_inactive.html", full_name=user.full_name,report_month = start_date.strftime("%B %Y"))
            else:
                data = process_user_data(attempts, purchases)
                
                html_content = render_template("monthly_report.html", full_name=user.full_name,report_month = start_date.strftime("%B %Y"), **data)

            # Send email
            msg = Message(
                subject="Your Monthly Activity Report from Quiz Master",
                sender="shibkumar1002@gmail.com",  # Update with your sender email
                recipients=[user.email],
                html=html_content
            )
            mail.send(msg)
            print(f"Report sent to {user.email}")
        except Exception as e:
            print(f"Error sending report to {user.email}: {e}")
                     
# Daily Reminder for New Quizzes
@celery_app.task(name="send_new_quiz_google_chat_notification")
def send_new_quiz_google_chat_notification():
    current_time = datetime.now(IST)
    recent_threshold = current_time - timedelta(hours=24)  # Check last 8 hours

    new_quizzes = Quiz.query.filter(
        Quiz.record_creation_timestamp > recent_threshold,
        Quiz.visibility == True
    ).all()

    if not new_quizzes:
        return  

    # Separate quizzes into free and paid
    free_quizzes = [quiz for quiz in new_quizzes if not quiz.pay_required]
    paid_quizzes = [quiz for quiz in new_quizzes if quiz.pay_required]

    # Send notification for Free Quizzes (if available)
    if free_quizzes:
        free_message_parts = [
            "🎉 *FREE Quizzes Just Arrived!* 🆓",
            "🔥 No cost, just pure challenge! Test your skills and rank up! 📚💡",
            ""
        ]

        for quiz in free_quizzes:
            subject_name = quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else "Mystery Subject"
            chapter_name = quiz.chapter.name if quiz.chapter else "Secret Chapter"
            duration = f"🕒 {quiz.time_duration} min of brain power!"

            free_quiz_details = (
                f"✅ *{subject_name}* | ✨ *{chapter_name}*\n"
                f"{duration} | 🆓 *Absolutely FREE!* 🎯\n"
            )

            free_message_parts.append(free_quiz_details)

        free_message_parts.append("🎯 *Why wait? Grab these free quizzes NOW!* 🚀")
        free_message = "\n".join(free_message_parts)

        send_group_msg_google_chat_space(free_message)
        print(f"Google Chat New Free Quiz Notification Send")

    # Send notification for Paid Quizzes (if available)
    if paid_quizzes:
        paid_message_parts = [
            "💎 *Exclusive Paid Quizzes Now LIVE!* 💰",
            "🔥 Premium challenges for serious learners! Prove your expertise & level up! 📚🏆",
            ""
        ]

        for quiz in paid_quizzes:
            subject_name = quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else "Premium Subject"
            chapter_name = quiz.chapter.name if quiz.chapter else "VIP Chapter"
            price = f"💰 *{quiz.pay_amount} Rupees*"
            duration = f"🕒 {quiz.time_duration} min of expert-level trivia!"

            paid_quiz_details = (
                f"🚀 *{subject_name}* | ✨ *{chapter_name}*\n"
                f"{duration} | {price} 🎯\n"
            )

            paid_message_parts.append(paid_quiz_details)

        paid_message_parts.append("⚡ *Limited-time premium quizzes! Are you ready?* 🚀")
        paid_message = "\n".join(paid_message_parts)

        send_group_msg_google_chat_space(paid_message)
        print(f"Google Chat New Paid Quiz Notification Sent")

# Daily Reminder for Quiz Endorsements
@celery_app.task(name="send_quiz_endorsement_google_chat_notification")
def send_quiz_endorsement_google_chat_notification():
    current_time = datetime.now(IST)
    three_days_ago = (current_time - timedelta(days=3)).replace(tzinfo=None)
    easy_quizzes = Quiz.query.filter(
        Quiz.visibility == True,
        Quiz.overall_difficulty.ilike("easy")
    ).all()
    
    free_endorsements = []
    paid_endorsements = []
    free_subjects = set()
    paid_subjects = set()
    
    for quiz in easy_quizzes:
        subject = quiz.chapter.subject if quiz.chapter and quiz.chapter.subject else None
        if not subject:
            continue  
        
        attempts_count = len(quiz.quiz_attempts)
        recent_sales = any(payment.created_at >= three_days_ago for payment in quiz.quiz_payments)
        if attempts_count < 2 or not recent_sales:
            if quiz.pay_required:
                if subject.id not in paid_subjects:
                    paid_endorsements.append(quiz)
                    paid_subjects.add(subject.id)
            else:
                if subject.id not in free_subjects:
                    free_endorsements.append(quiz)
                    free_subjects.add(subject.id)
    
    # Prepare and send notification for Free Quizzes (if any)
    if free_endorsements:
        free_message_parts = [
            "🎉 *Hidden Gem FREE Quizzes!* 🆓",
            "These easy challenges are underplayed – why not give them a try and boost your skills? 🚀",
            ""
        ]
        for quiz in free_endorsements:
            subject_name = quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else "Unknown Subject"
            chapter_name = quiz.chapter.name if quiz.chapter else "Unknown Chapter"
            duration = f"🕒 {quiz.time_duration} min"
            
            quiz_details = (
                f"📚 *{subject_name}* | 🔍 *{chapter_name}*\n"
                f"{duration} of brain power! | 🆓 FREE\n"
            )
            free_message_parts.append(quiz_details)
        free_message_parts.append("👉 Jump in and give these free gems some love!")
        free_message = "\n".join(free_message_parts)
        
        send_group_msg_google_chat_space(free_message)
        print(f"Google Chat Free Endorsement Notification Sent")
    
    # Prepare and send notification for Paid Quizzes (if any)
    if paid_endorsements:
        paid_message_parts = [
            "💎 *Exclusive Hidden Gem Paid Quizzes!* 💰",
            "Premium challenges that are waiting to be discovered – show off your expertise! 🏆",
            ""
        ]
        for quiz in paid_endorsements:
            subject_name = quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else "Unknown Subject"
            chapter_name = quiz.chapter.name if quiz.chapter else "Unknown Chapter"
            duration = f"🕒 {quiz.time_duration} min"
            price = f"💰 {quiz.pay_amount} Rupees"
            
            quiz_details = (
                f"📚 *{subject_name}* | 🔍 *{chapter_name}*\n"
                f"{duration} | {price} \n"
            )
            paid_message_parts.append(quiz_details)
        paid_message_parts.append("⚡ Don't miss out on these exclusive challenges!")
        paid_message = "\n".join(paid_message_parts)
        
        send_group_msg_google_chat_space(paid_message)
        print(f"Google Chat Paid Endorsement Notification Sent")

# Export Quiz Attempts to CSV for specific user
@celery_app.task(name="export_quiz_attempts_to_csv")
def export_quiz_attempts_to_csv(user_id, user_email):
    try:
        csv_headers, csv_rows = generate_quiz_attempts_csv(user_id)
        csv_filename = f"quiz_attempts_user_{user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        csv_filepath = os.path.join('/tmp_csvs', csv_filename)
        os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)
        if not csv_rows:
            html_content = render_template(
                "quiz_export.html",
                has_quiz_attempts=False,
                message="No quiz attempts found in your account."
            )
            with open(csv_filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(csv_headers)
                writer.writerow(["No quiz attempts recorded"] + [""] * (len(csv_headers) - 1))
        else:
            html_content = render_template(
                "quiz_export.html",
                has_quiz_attempts=True,
                message="Your quiz attempts export is ready!"
            )
            with open(csv_filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(csv_headers)
                for row in csv_rows:
                    writer.writerow(row)
        # Prepare and send email
        email_message = Message(
            subject="Your Quiz Attempts Export CSV is Ready",
            sender=SENDER_MAIL,
            recipients=[user_email],
            html=html_content
        )
        with open(csv_filepath, 'rb') as f:
            email_message.attach(csv_filename, 'text/csv', f.read())
        mail.send(email_message)
        print(f"Quiz export email sent to {user_email}")
        os.remove(csv_filepath)
    except Exception as e:
        print(f"Error in export task: {str(e)}")
  
# Export All Users Quiz Data to CSV for Admin      
@celery_app.task(name="export_all_users_quiz_data_to_csv")
def export_all_users_quiz_data_to_csv(admin_id, admin_email):
    try:
        csv_headers, csv_rows = generate_all_users_quiz_data_csv(admin_id)
        csv_filename = f"all_users_quiz_data_{admin_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        csv_filepath = os.path.join('/tmp_csvs', csv_filename)
        os.makedirs(os.path.dirname(csv_filepath), exist_ok=True)

        if not csv_rows:
            html_content = render_template(
                "admin_quiz_export.html",
                has_quiz_attempts=False,
                message="No quiz data found for users."
            )
            with open(csv_filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(csv_headers)
                writer.writerow(["No quiz data recorded"] + [""] * (len(csv_headers) - 1))
        else:
            html_content = render_template(
                "admin_quiz_export.html",
                has_quiz_attempts=True,
                message="All users' quiz data export is ready!"
            )
            with open(csv_filepath, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(csv_headers)
                for row in csv_rows:
                    writer.writerow(row)

        # Send email with CSV attachment
        email_message = Message(
            subject="All Users Quiz Data Export CSV",
            sender=SENDER_MAIL,  # Replace with your sender email
            recipients=[admin_email],
            html=html_content
        )
        with open(csv_filepath, 'rb') as f:
            email_message.attach(csv_filename, 'text/csv', f.read())
        mail.send(email_message)
        print(f"Quiz data export email sent to {admin_email}")
        os.remove(csv_filepath)

    except Exception as e:
        print(f"Error in export task: {str(e)}")
           
# Periodic Task Scheduling
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Daily Reminder at 9 AM IST
    sender.add_periodic_task(
        crontab(hour=9, minute=0),
        # crontab(minute='*/1'),  # Runs every minute for testing only
        send_daily_reminder.s(),
        name="daily-reminder"
    )

    # Monthly Report on 1st of every month at 9 AM IST
    sender.add_periodic_task(
        crontab(day_of_month=1, hour=9, minute=0),
        # crontab(minute='*/1'),  # Runs every minute for testing only
        send_monthly_report.s(),
        name="monthly-report"
    )

    # Google Chat Notifications (3 times daily: 9 AM, 1 PM, 5 PM IST)
    sender.add_periodic_task(
        crontab(hour=9, minute=0),
        # crontab(minute='*/1'),   # Runs every minute for testing only
        send_new_quiz_google_chat_notification.s(),
        name="new-quiz-google-chat-notification-morning"
    )
    sender.add_periodic_task(
        crontab(hour=13, minute=0),
        send_new_quiz_google_chat_notification.s(),
        name="new-quiz-google-chat-notification-afternoon"
    )
    sender.add_periodic_task(
        crontab(hour=17, minute=0),
        send_new_quiz_google_chat_notification.s(),
        name="new-quiz-google-chat-notification-evening"
    )
    
    sender.add_periodic_task(
        crontab(hour=9, minute=0),
        # crontab(minute='*/1'),  # Runs every minute for testing only
        send_quiz_endorsement_google_chat_notification.s(),
        name="send-quiz-endorsement-google-chat-notification"
    )
    
    