# Quiz Master

## Introduction
Quiz Master is a robust, single-page application (SPA) designed for exam preparation, supporting an Admin (superuser) and multiple Users. It enables course management, quiz creation, proctored assessments, and performance tracking. Built with a modern technology stack, it ensures scalability, security, and seamless local demo functionality.

## Technology Stack
- **Backend**: Flask (powers API endpoints), SQLite (data storage), Redis (caching for speed), Celery (schedules background tasks).
- **Frontend**: VueJS (dynamic SPA interface), VueJS Advanced with CLI (build tools), Bootstrap (responsive styling).
- **Templating**: Jinja2 (initial page load only).
- **Libraries**: ChartJS (visual charts), Flask-Mail (email notifications), Google Chat Webhooks (chat alerts), Stripe (payment processing), Axios (API communication).

## System Architecture
- **Backend**: Flask handles request-response cycles, serving RESTful APIs. SQLite stores data with SQLAlchemy, Redis caches responses, and Celery schedules tasks like email reminders.
- **Frontend**: VueJS operates as a Single-Page Application (SPA), loading once and updating dynamically via Axios HTTP requests to the backend. Bootstrap ensures a responsive layout across devices.
- **Authentication**: JWT (JSON Web Tokens) secures endpoints, assigning tokens to distinguish Admin and User roles.
- **Request-Response**: Axios sends requests (e.g., GET for quiz data, POST for submissions) and processes JSON responses from Flask APIs.

## Roles and Functionalities

### Admin (Quiz Master)
- **Access**: Logs in with pre-existing superuser credentials; redirects to admin dashboard.
- **Functionalities**:
  - **Content Management**: Creates, updates, and deletes subjects, chapters, quizzes, and questions using CRUD operations. Attributes include name, description, time_duration, and pay_required.
  - **Dashboard**: Displays real-time stats (user count, quiz totals, revenue) and ChartJS visuals (e.g., performance trends, engagement metrics).
  - **Search and Pagination**: Filters content (e.g., by subject name) and paginates lists for easy navigation.
  - **Reports**: Generates and downloads CSV reports, including system summaries, subject analyses, revenue breakdowns, quiz popularity, and all quiz data.

### User
- **Access**: Registers with username (email), password, full_name, etc.; logs in to access features.
- **Functionalities**:
  - **Quiz Participation**: Browses subjects/chapters, selects quizzes (proctored or regular), and starts attempts via Axios calls.
  - **Proctored Exams**: Includes timers, tab-switching detection (3-strike limit), and event logging to ensure fairness.
  - **Performance Tracking**: Views scores, with options to sort (e.g., by date), search (e.g., by subject), paginate results, and download attempts or insights as CSV files.
  - **Dashboard**: Shows performance, mastery, and engagement through interactive charts.

## Core Features
- **SPA Design**: VueJS delivers a fast, single-page experience with no full page reloads.
- **Secure Login**: JWT tokens authenticate requests, ensuring role-based access.
- **Proctored Quizzes**: Monitors tab switches and logs actions for integrity.
- **Search and Pagination**: Simplifies finding and browsing content or results.
- **Responsive UI**: Bootstrap adapts the interface for phones and desktops.
- **Payments via Stripe**: Enables secure purchases of premium quizzes.
- **Performance Boost**: Redis caches API responses; Celery runs tasks like notifications asynchronously.

## Scheduled Tasks (Celery with Crontab)
- **Daily Emails**: Sent at 9 AM IST to remind Users of new quizzes.
- **Monthly Reports**: Emails detailed quiz stats on the 1st of each month.
- **Google Chat Alerts**: Notifies about new or featured quizzes at 9 AM, 1 PM, and 5 PM IST via webhooks.
- **Reports (CSV) Downloads**: Admin exports all quiz data; Users export personal attempts.

## Database Schema (SQLite)
- **Users**: Stores user profile (e.g., email, full_name) and links to quiz attempts and payments.
- **Admins**: Holds superuser details (e.g., username, password).
- **Subjects**: Lists topics like “Physics.”
- **Chapters**: Breaks subjects into sections like “Mechanics.”
- **Quizzes**: Saves quiz details (e.g., date_of_quiz, time_duration).
- **Questions**: Stores questions and answers (e.g., question_statement, correct_option).
- **QuizAttempts**: Tracks user quiz  quiz tries (e.g., total_score, total_time_taken).
- **QuestionAttempts**: Records user answer choices (e.g., selected_option).
- **UserActivity**: Logs actions like logins (e.g., activity_type).
- **QuizEventLogs**: Watches proctored quiz events (e.g., event_type).
- **QuizPayments**: Tracks payments (e.g., amount_paid, payment_status).
- **QuizCarts**: Lists quizzes users’ve selected to buy (e.g., quiz_id).

## Extra Features
- **Charts**: Visualizes progress with ChartJS.
- **Notifications**: Emails (payments, results) via Flask-Mail; Google Chat for quiz updates.
- **Input Validation**: Checks data on both frontend and backend.

## Getting Started
Follow these steps to set up and run Quiz Master locally:

1. **Create a Virtual Environment**:
   ```bash
   cd backend
   python -m venv venv
   ```
   This creates a virtual environment named `venv` in your project directory.

2. **Activate the Virtual Environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

3. **Install Backend Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   Ensure you have a `requirements.txt` file listing all Python dependencies (e.g., Flask, SQLAlchemy, Celery, etc.).

4. **Set Up the Database**:
   ```bash
   python .\setup_db.py
   ```

5. **Start the Backend Server**:
   ```bash
   python .\app.py
   ```
6. **Run Redis Server for Caching and Background Tasks**:
   ```bash
   redis-server  
   ```

7. **Run Celery Worker for Background Tasks**:
   ```bash
   celery -A celery_worker.celery_app worker --pool=threads --loglevel=info
   ```

8. **Run Celery Beat for Scheduled Tasks**:
   ```bash
   celery -A celery_worker.celery_app beat --loglevel=info
   ```

9. **Start the Frontend Development Server**:
   ```bash
   cd frontend
   npm run dev
   ```
   Note: Ensure you have Node.js and npm installed, and run `npm install` in the `frontend` directory if dependencies are not yet installed.

**Important**: Run each service (Flask app, Celery worker, Celery beat, and VueJS dev server) in separate terminal instances.

## Conclusion
Quiz Master is a professional SPA with secure authentication, proctored quizzes, and optimized performance. It’s a complete solution for exam preparation and administration.
