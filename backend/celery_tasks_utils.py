from datetime import datetime, timedelta
import pytz
from dateutil.relativedelta import relativedelta
from model import QuizAttempt, Quiz, Chapter, Subject, QuizPayment,db, User
import csv
from io import StringIO
import os
IST = pytz.timezone('Asia/Kolkata')

def process_daily_reminder_data():
    try:
        current_time = datetime.now(IST)
        inactive_threshold = (current_time - timedelta(days=1)).replace(tzinfo=None)
        
        # Fetch new quizzes (last 24 hours)
        new_quizzes = Quiz.query.filter(
            Quiz.record_creation_timestamp > inactive_threshold,
            Quiz.visibility == True
        ).all()

        # Fetch endorsement quizzes (easy, underplayed quizzes)
        three_days_ago = (current_time - timedelta(days=3)).replace(tzinfo=None)
        endorse_quizzes = Quiz.query.filter(
            Quiz.visibility == True,
            Quiz.overall_difficulty.ilike("easy")
        ).all()

        # Separate new quizzes
        new_free_quizzes_all = [quiz for quiz in new_quizzes if not quiz.pay_required]
        new_paid_quizzes_all = [quiz for quiz in new_quizzes if quiz.pay_required]

        # Separate endorsement quizzes
        free_endorsements = []
        paid_endorsements = []
        free_subjects = set()
        paid_subjects = set()
        for quiz in endorse_quizzes:
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

        # Helper function to group quizzes by subject
        def group_by_subject(quizzes, limit=2):
            groups = {}
            for quiz in quizzes:
                subject = quiz.chapter.subject.name if quiz.chapter and quiz.chapter.subject else "Unknown Subject"
                groups.setdefault(subject, []).append(quiz)
            data = []
            for subject, group in groups.items():
                count = len(group)
                selected = group[:limit]
                for quiz in selected:
                    data.append({
                        "subject": subject,
                        "chapter": quiz.chapter.name if quiz.chapter else "Unknown Chapter",
                        "name": f"Quiz #{quiz.id}",
                        "level": quiz.overall_difficulty.capitalize() if quiz.overall_difficulty else "N/A",
                        "amount": "Free" if not quiz.pay_required else f"{quiz.pay_amount} Coins"
                    })
                extra = count - len(selected)
                if extra > 0:
                    data.append({
                        "subject": subject,
                        "chapter": "",
                        "name": f"And {extra} more quizzes in {subject}...",
                        "level": "",
                        "amount": ""
                    })
            return data

        new_free_quizzes_data = group_by_subject(new_free_quizzes_all, limit=2)
        new_paid_quizzes_data = group_by_subject(new_paid_quizzes_all, limit=2)
        endorse_free_quizzes_data = group_by_subject(free_endorsements, limit=2)
        endorse_paid_quizzes_data = group_by_subject(paid_endorsements, limit=2)
        
        return (new_free_quizzes_data, new_paid_quizzes_data, endorse_free_quizzes_data, 
                endorse_paid_quizzes_data, inactive_threshold)
    except Exception as e:
        print(f"Error in data processing: {e}")
        return None, None, None, None, None

def generate_quiz_attempts_csv(user_id):
    try:
        query = (
            db.session.query(QuizAttempt, Quiz, Chapter, Subject)
            .join(Quiz, QuizAttempt.quiz_id == Quiz.id, isouter=True)
            .join(Chapter, Quiz.chapter_id == Chapter.id, isouter=True)
            .join(Subject, Chapter.subject_id == Subject.id, isouter=True)
            .filter(QuizAttempt.user_id == user_id)
            .order_by(Quiz.date_of_quiz.asc())  
        ).all()

        # Define CSV headers
        csv_headers = [
            "Attempt ID", "Quiz ID", "Subject Name", "Chapter Name", "Date of Quiz",
            "Score Earned", "Full Marks", "Performance", "Total Correct Answers",
            "Total Questions", "Time Taken (s)", "Remarks"
        ]

        csv_rows = []
        for idx, (qa, q, c, s) in enumerate(query):
            attempt_id = idx + 1  # Ascending order: 1, 2, 3, ...
            score_percentage = (qa.total_score_earned / qa.total_score * 100) if qa.total_score > 0 else 0
            performance = (
                'Outstanding' if score_percentage >= 75 else
                'Good' if score_percentage >= 50 else
                'Pass' if score_percentage >= 25 else
                'Fail'
            )
            remarks = "Completed" if qa.quiz_end_time else "Incomplete"
            row = [
                attempt_id,
                qa.quiz_id if qa.quiz_id else 'N/A',
                s.name if s else 'N/A',
                c.name if c else 'N/A',
                q.date_of_quiz.strftime('%Y-%m-%d') if q and q.date_of_quiz else 'N/A',
                qa.total_score_earned,
                qa.total_score,
                performance,
                qa.total_correct_ans,
                qa.total_questions_count,
                qa.total_time_taken,
                remarks
            ]
            csv_rows.append(row)

        return csv_headers, csv_rows

    except Exception as e:
        print(f"Error generating quiz attempts CSV for user {user_id}: {str(e)}")
        return [], []
    
    
def generate_all_users_quiz_data_csv(admin_id):
    try:
        # Query all users and their quiz attempts filtered by admin_id
        users = User.query.all()
        csv_headers = [
            "User ID", "Username", "Email", "Quizzes Taken", "Average Score", "Average Performance",
            "Total Correct Answers", "Total Questions Attempted", "Average Time Taken (s)"
        ]
        csv_rows = []

        for user in users:
            quiz_attempts = (
                db.session.query(QuizAttempt)
                .join(Quiz, QuizAttempt.quiz_id == Quiz.id)
                .filter(QuizAttempt.user_id == user.id, Quiz.admin_id == admin_id)
                .all()
            )
            if not quiz_attempts:
                continue  # Skip users with no quiz attempts under this admin

            quizzes_taken = len(quiz_attempts)
            total_score = sum(qa.total_score_earned for qa in quiz_attempts)
            total_max_score = sum(qa.total_score for qa in quiz_attempts)
            total_correct = sum(qa.total_correct_ans for qa in quiz_attempts)
            total_questions = sum(qa.total_questions_count for qa in quiz_attempts)
            total_time = sum(qa.total_time_taken for qa in quiz_attempts)

            avg_score = total_score / quizzes_taken if quizzes_taken > 0 else 0
            avg_time = total_time / quizzes_taken if quizzes_taken > 0 else 0
            avg_percentage = (total_score / total_max_score * 100) if total_max_score > 0 else 0
            avg_performance = (
                'Outstanding' if avg_percentage >= 75 else
                'Good' if avg_percentage >= 50 else
                'Pass' if avg_percentage >= 25 else
                'Fail'
            )

            row = [
                user.id,
                user.username,
                user.email,
                quizzes_taken,
                round(avg_score, 2),
                avg_performance,
                total_correct,
                total_questions,
                round(avg_time, 2)
            ]
            csv_rows.append(row)

        return csv_headers, csv_rows

    except Exception as e:
        print(f"Error generating all users quiz data CSV: {str(e)}")
        return [], []
    
def get_previous_month_range():
    current_date = datetime.now(pytz.timezone("Asia/Kolkata"))
    first_day_current_month = current_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    last_day_previous_month = first_day_current_month - timedelta(days=1)
    first_day_previous_month = last_day_previous_month.replace(day=1)
    return first_day_previous_month, last_day_previous_month


def get_user_activity(user, start_date, end_date):
    # Query quiz attempts with related data
    attempts = db.session.query(
        QuizAttempt, Quiz, Chapter, Subject
    ).join(
        Quiz, QuizAttempt.quiz_id == Quiz.id
    ).join(
        Chapter, Quiz.chapter_id == Chapter.id
    ).join(
        Subject, Chapter.subject_id == Subject.id
    ).filter(
        QuizAttempt.user_id == user.id,
        QuizAttempt.record_creation_timestamp >= start_date,
        QuizAttempt.record_creation_timestamp <= end_date
    ).all()

    # Query purchases
    purchases = QuizPayment.query.filter(
        QuizPayment.user_id == user.id,
        QuizPayment.payment_status == 'Completed',
        QuizPayment.created_at >= start_date,
        QuizPayment.created_at <= end_date
    ).all()

    return attempts, purchases


def process_user_data(attempts, purchases):
    quiz_data = {}
    subject_scores = {}
    chapter_scores = {}
    free_quizzes = set()
    total_attempts = 0

    # Process quiz attempts
    for attempt, quiz, chapter, subject in attempts:
        quiz_id = quiz.id
        subject_name = subject.name
        chapter_name = chapter.name
        score = attempt.total_score
        attempt_date = attempt.record_creation_timestamp

        # Group by quiz
        if quiz_id not in quiz_data:
            quiz_data[quiz_id] = {
                'subject_name': subject_name,
                'chapter_name': chapter_name,
                'attempts': [],
                'pay_required': quiz.pay_required
            }
        quiz_data[quiz_id]['attempts'].append({
            'date': attempt_date.strftime("%Y-%m-%d"),
            'score': score
        })
        total_attempts += 1

        # Aggregate by subject
        if subject_name not in subject_scores:
            subject_scores[subject_name] = []
        subject_scores[subject_name].append(score)

        # Aggregate by chapter
        chapter_key = f"{subject_name} - {chapter_name}"
        if chapter_key not in chapter_scores:
            chapter_scores[chapter_key] = []
        chapter_scores[chapter_key].append(score)

        # Track free quizzes
        if not quiz.pay_required:
            free_quizzes.add(quiz_id)

    # Calculate quiz metrics
    for quiz_id, data in quiz_data.items():
        scores = [attempt['score'] for attempt in data['attempts']]
        data['num_attempts'] = len(scores)
        data['highest_score'] = max(scores) if scores else 0
        data['average_score'] = sum(scores) / len(scores) if scores else 0

    # Calculate subject and chapter performance
    subject_performance = {subject: sum(scores) / len(scores) for subject, scores in subject_scores.items()}
    chapter_performance = {chapter: sum(scores) / len(scores) for chapter, scores in chapter_scores.items()}

    # Process purchases
    purchase_details = []
    total_amount_spent = 0
    for purchase in purchases:
        purchase_details.append({
            'quiz_id': purchase.quiz_id,
            'amount_paid': purchase.amount_paid
        })
        total_amount_spent += purchase.amount_paid

    return {
        'unique_quizzes_attempted': len(quiz_data),
        'total_attempts': total_attempts,
        'total_quizzes_purchased': len(purchases),
        'total_amount_spent': total_amount_spent,
        'quiz_details': quiz_data,
        'purchases': purchase_details,
        'free_quizzes': list(free_quizzes),
        'subject_performance': subject_performance,
        'chapter_performance': chapter_performance
    }