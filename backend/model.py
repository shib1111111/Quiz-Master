from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz

# Initialize SQLAlchemy
db = SQLAlchemy()

def get_current_ist():
    """Returns the current datetime in Asia/Kolkata timezone."""
    return datetime.now(pytz.timezone("Asia/Kolkata"))

# User Model
class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True, index=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    qualification = db.Column(db.String)
    dob = db.Column(db.String)
    signup_timestamp = db.Column(db.DateTime, default=get_current_ist)
    
    # Relationships (no cascading deletion for user history)
    quiz_attempts = db.relationship('QuizAttempt', backref='user', lazy=True)
    activities = db.relationship('UserActivity', backref='user', lazy=True)
    question_attempts = db.relationship('QuestionAttempt', backref='user', lazy=True)
    quiz_event_logs = db.relationship('QuizEventLog', backref='user', lazy=True)
    quiz_payments = db.relationship('QuizPayment', backref='user', lazy=True)
    quiz_carts = db.relationship('QuizCart', backref='user', lazy=True)

# Admin Model
class Admin(db.Model):
    __tablename__ = 'admins'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False, unique=True, index=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    full_name = db.Column(db.String, nullable=False)
    signup_timestamp = db.Column(db.DateTime, default=get_current_ist)
    
    # Relationships for records created by Admin (no cascading deletion needed here)
    subjects = db.relationship('Subject', backref='admin', lazy=True)
    chapters = db.relationship('Chapter', backref='admin', lazy=True)
    quizzes = db.relationship('Quiz', backref='admin', lazy=True)
    questions = db.relationship('Question', backref='admin', lazy=True)

# Subject Model (created by Admin)
class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.Text)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False, index=True)
    record_creation_timestamp = db.Column(db.DateTime, default=get_current_ist)
    
    # Cascade deletion for admin-managed chapters
    chapters = db.relationship('Chapter', backref='subject', lazy=True, cascade='all, delete-orphan')

# Chapter Model (created by Admin)
class Chapter(db.Model):
    __tablename__ = 'chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False, index=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False, index=True)
    name = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    record_creation_timestamp = db.Column(db.DateTime, default=get_current_ist)
    
    # Cascade deletion for admin-managed quizzes
    quizzes = db.relationship('Quiz', backref='chapter', lazy=True, cascade='all, delete-orphan')

# Quiz Model (created by Admin)
class Quiz(db.Model):
    __tablename__ = 'quizzes'
    
    id = db.Column(db.Integer, primary_key=True)
    chapter_id = db.Column(db.Integer, db.ForeignKey('chapters.id', ondelete='CASCADE'), nullable=False, index=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False, index=True)
    date_of_quiz = db.Column(db.Date, nullable=False, index=True)
    time_duration = db.Column(db.Integer, nullable=False)
    overall_difficulty = db.Column(db.Text)
    visibility = db.Column(db.Boolean, nullable=False, default=True)
    pay_required = db.Column(db.Boolean, nullable=False, default=False)
    pay_amount = db.Column(db.Float, nullable=False, default=0.0)
    record_creation_timestamp = db.Column(db.DateTime, default=get_current_ist)
    
    # Cascade deletion for admin-managed questions
    questions = db.relationship('Question', backref='quiz', lazy=True, cascade='all, delete-orphan')
    quiz_attempts = db.relationship('QuizAttempt', backref='quiz', lazy=True)
    quiz_payments = db.relationship('QuizPayment', backref='quiz', lazy=True)
    quiz_carts = db.relationship('QuizCart', backref='quiz', lazy=True)
class QuizPayment(db.Model):
    __tablename__ = 'quiz_payments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True, index=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id', ondelete='SET NULL'), nullable=True, index=True)
    amount_paid = db.Column(db.Float, nullable=False, default=0.0)
    payment_status = db.Column(db.Enum('Pending', 'Completed', 'Failed', name='payment_status_enum'), default='Pending', nullable=False)
    payment_method = db.Column(db.String, nullable=True)
    transaction_id = db.Column(db.String, unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)

class QuizCart(db.Model):
    __tablename__ = 'quiz_carts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True, index=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=True, index=True)
    created_at = db.Column(db.DateTime, default=get_current_ist)
    updated_at = db.Column(db.DateTime, default=get_current_ist, onupdate=get_current_ist)
    __table_args__ = (
        db.UniqueConstraint('user_id', 'quiz_id', name='uq_user_quiz_cart'),
    )
# Question Model (created by Admin)
class Question(db.Model):
    __tablename__ = 'questions'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id', ondelete='CASCADE'), nullable=False, index=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('admins.id'), nullable=False, index=True)
    question_statement = db.Column(db.Text, nullable=False)
    option1 = db.Column(db.String, nullable=False)
    option2 = db.Column(db.String, nullable=False)
    option3 = db.Column(db.String, nullable=False)
    option4 = db.Column(db.String, nullable=False)
    correct_option = db.Column(db.String, nullable=False)
    difficulty = db.Column(db.String, nullable=False, default='easy', index=True)
    score_value = db.Column(db.Integer, nullable=False, default=1)
    record_creation_timestamp = db.Column(db.DateTime, default=get_current_ist)
    
    # No cascading deletion for user question attempts (history preserved)
    question_attempts = db.relationship('QuestionAttempt', backref='question', lazy=True)
    quiz_event_logs = db.relationship('QuizEventLog', backref='question', lazy=True)

    def __init__(self, *args, **kwargs):
        super(Question, self).__init__(*args, **kwargs)
        if self.difficulty.lower() == 'easy':
            self.score_value = 1
        elif self.difficulty.lower() == 'medium':
            self.score_value = 2
        elif self.difficulty.lower() == 'hard':
            self.score_value = 4
        else:
            self.score_value = 1

# QuizAttempt Model (user-generated)
class QuizAttempt(db.Model):
    __tablename__ = 'quiz_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    quiz_id = db.Column(db.Integer, db.ForeignKey('quizzes.id', ondelete='SET NULL'), nullable=True, index=True)  # Allow NULL to preserve history
    total_questions_count = db.Column(db.Integer, nullable=False, default=0)
    total_score = db.Column(db.Integer, nullable=False, default=0)
    total_attempted_qn = db.Column(db.Integer, nullable=False, default=0)
    total_clicked = db.Column(db.Integer, nullable=False, default=0)
    total_correct_ans = db.Column(db.Integer, nullable=False, default=0)
    total_wrong_ans = db.Column(db.Integer, nullable=False, default=0)
    total_marked_for_review_qn = db.Column(db.Integer, nullable=False, default=0)
    total_skipped_qn = db.Column(db.Integer, nullable=False, default=0)
    total_deleted_ans = db.Column(db.Integer, nullable=False, default=0)
    total_score_earned = db.Column(db.Float, nullable=False, default=0.0)
    total_time_taken = db.Column(db.Integer, nullable=False, default=0)
    quiz_start_time = db.Column(db.DateTime)
    quiz_end_time = db.Column(db.DateTime)
    access_token = db.Column(db.String, nullable=True)  
    record_creation_timestamp = db.Column(db.DateTime, default=get_current_ist)
    
    # Cascade deletion for user-managed question attempts
    question_attempts = db.relationship('QuestionAttempt', backref='quiz_attempt', lazy=True, cascade='all, delete-orphan')
    quiz_event_logs = db.relationship('QuizEventLog', backref='quiz_attempt', lazy=True, cascade='all, delete-orphan')

# QuestionAttempt Model (user-generated)
class QuestionAttempt(db.Model):
    __tablename__ = 'question_attempts'
    
    id = db.Column(db.Integer, primary_key=True)
    quiz_attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id', ondelete='CASCADE'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='SET NULL'), nullable=True, index=True)  # Allow NULL to preserve history
    selected_option = db.Column(db.String, nullable=False)
    question_attempt_timestamp = db.Column(db.DateTime, nullable=False, default=get_current_ist)

# UserActivity Model (user-generated)
class UserActivity(db.Model):
    __tablename__ = 'user_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    user_role = db.Column(db.String, nullable=False)
    activity_type = db.Column(db.String, nullable=False)
    client_ip = db.Column(db.String, nullable=False)
    mac_address = db.Column(db.String, nullable=True)
    os_info = db.Column(db.String, nullable=True)
    browser = db.Column(db.String, nullable=True)
    device = db.Column(db.String, nullable=True)
    user_agent = db.Column(db.Text, nullable=True)
    memory_gb = db.Column(db.Float, nullable=True)
    cpu_cores = db.Column(db.Integer, nullable=True)
    record_creation_timestamp = db.Column(db.DateTime, default=get_current_ist)

# QuizEventLog Model (user-generated)
class QuizEventLog(db.Model):
    __tablename__ = 'quiz_event_logs'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    quiz_attempt_id = db.Column(db.Integer, db.ForeignKey('quiz_attempts.id', ondelete='CASCADE'), nullable=False, index=True)
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id', ondelete='SET NULL'), nullable=True, index=True)  # Already nullable
    event_type = db.Column(db.String, nullable=False)
    event_timestamp = db.Column(db.DateTime, nullable=False, default=get_current_ist)
    event_details = db.Column(db.Text, nullable=True)
    record_creation_timestamp = db.Column(db.DateTime, nullable=False, default=get_current_ist)