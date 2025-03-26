# /celery_tasks.py
from celery_worker import celery_app
from flask_mail import Message
from app import mail



@celery_app.task(name="send_reset_password_email")
def send_reset_password_email(recipient_email, one_time_password="default_otp"):
    # Create email message
    email_message = Message(
        subject="Password Reset Request",
        sender="shibkumar1002@gmail.com",  # Update with your sender email
        recipients=[recipient_email]
    )
    email_message.body = (
        f"To reset your password, use this OTP: {one_time_password}\n\n"
        f"If you didn’t request a password reset, please ignore this email."
    )
    
    # Send the email
    mail.send(email_message)
    print(f"Password reset email sent to {recipient_email}")
    
@celery_app.task(name="send_reset_password_success_email")
def send_reset_password_success_email(recipient_email):
    # Create email message
    email_message = Message(
        subject="Password Reset Successful",
        sender="shibkumar1002@gmail.com",  # Update with your sender email
        recipients=[recipient_email]
    )
    
    email_message.body = (
        f"Your password has been successfully reset.\n\n"
        f"If you didn’t reset your password, please contact support."
    )
    
    # Send the email
    mail.send(email_message)
    print(f"Password reset email sent to {recipient_email}")    
    
@celery_app.task
def daily_reminder():
    # Implement your reminder logic here
    print("Daily reminder task executed")

@celery_app.task
def mark_overdue_requests_as_revoked():
    # Implement your overdue check here
    print("Marking overdue requests as revoked")

@celery_app.task
def send_monthly_report():
    # Implement your monthly report logic here
    print("Monthly report sent")

# Set up periodic tasks (using simple intervals for demonstration)
@celery_app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    # Run daily_reminder every 30 seconds (adjust as needed)
    sender.add_periodic_task(30.0, daily_reminder.s(), name="daily reminder every 30 sec")
    
    # Run mark_overdue_requests_as_revoked every 60 seconds
    sender.add_periodic_task(60.0, mark_overdue_requests_as_revoked.s(), name="mark overdue every 60 sec")
    
    # Run send_monthly_report every 30 seconds (for demo; in production use a crontab schedule)
    sender.add_periodic_task(30.0, send_monthly_report.s(), name="monthly report every 30 sec")
