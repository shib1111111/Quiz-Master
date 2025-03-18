
# Quiz Master - V2

Quiz Master - V2 is a multi-user exam preparation platform that allows an administrator (Quiz Master) to manage subjects, chapters, quizzes, and questions while providing users with an interactive interface to attempt quizzes and track their performance.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Installation](#installation)
- [Usage](#usage)
- [Scheduled and Async Jobs](#scheduled-and-async-jobs)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Overview

Quiz Master - V2 is designed to help students prepare for exams across multiple courses by offering a streamlined platform for quiz creation, management, and participation. The application is built on a modular architecture with two distinct roles:

- **Admin (Quiz Master):** A pre-existing superuser with root access to create subjects, chapters, quizzes, and manage all users.
- **User:** Can register, login, attempt quizzes, and view their scores and performance history.

## Features

- **Role-Based Access Control:** Only one admin (Quiz Master) exists, while users can self-register.
- **Subject & Chapter Management:** Admin can create/edit/delete subjects and chapters.
- **Quiz Management:** Create quizzes with multiple-choice questions (one correct option) under each chapter.
- **User Quiz Experience:** 
  - Register/Login
  - Attempt quizzes with a built-in timer
  - View quiz scores and historical attempts
  - Display summary charts for performance
- **Automated Notifications & Reports:**
  - Daily reminders for inactive users or when a new quiz is added.
  - Monthly activity reports (HTML or PDF) sent via email.
- **Async Batch Jobs:**
  - Export quiz details as CSV (triggered by both admin and users).
- **Performance and Caching:** 
  - Integrated Redis for caching with expiry settings.
  - Redis and Celery to handle batch jobs.

## Tech Stack

- **Backend:** 
  - Flask (API)
  - SQLite (database)
  - Redis (caching)
  - Celery (batch job management)
- **Frontend:** 
  - VueJS (UI)
  - VueJS Advanced with CLI (optional)
  - Bootstrap (styling)
- **Templating:** 
  - Jinja2 (for CDN-based entry point only; not for UI rendering)

## Project Structure

```
Quiz_Master/
├── backend/
│   ├── app.py                  # Flask API entry point
│   ├── models.py               # Database models and schema (SQLite)
│   ├── routes/                 # API routes (user, admin, quiz management)
│   ├── celery_worker.py        # Celery configuration and scheduled jobs
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── public/
│   ├── src/
│   │   ├── components/         # VueJS components for various views
│   │   ├── App.vue             # Main Vue component
│   │   └── main.js             # VueJS application entry point
│   ├── package.json            # Node dependencies and scripts
│   └── README.md               # Frontend-specific instructions (if needed)
└── README.md                   # This file
```

> **Note:** The database and tables are created programmatically during the application initialization. Manual creation (e.g., using DB Browser for SQLite) is not allowed.

## Installation

### Prerequisites

- Python 3.x
- Node.js and npm
- Redis
- SQLite

### Backend Setup

1. **Clone the repository:**

   ```bash
   git clone https://github.com/21f1001520/quiz_master_21f1001520.git
   cd quiz_master_21f1001520/backend
   ```

2. **Create a virtual environment and install dependencies:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables:**

   Create a `.env` file in the `backend` folder with variables such as:

   ```env
   FLASK_APP=app.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   DATABASE_URI=sqlite:///quiz_master.db
   REDIS_URL=redis://localhost:6379/0
   CELERY_BROKER_URL=redis://localhost:6379/0
   CELERY_RESULT_BACKEND=redis://localhost:6379/0
   ```

4. **Initialize the Database:**

   The database schema will be created programmatically on the first run.

5. **Start the Flask Server:**

   ```bash
   flask run
   ```

### Frontend Setup

1. **Navigate to the frontend directory:**

   ```bash
   cd ../frontend
   ```

2. **Install dependencies:**

   ```bash
   npm install
   ```

3. **Configure Environment Variables (if required):**

   Create a `.env` file in the `frontend` folder with any necessary variables (e.g., API endpoint).

4. **Start the VueJS Development Server:**

   ```bash
   npm run serve
   ```

## Usage

- **Admin (Quiz Master):**
  - The admin account is pre-created in the database. Use these credentials to log in and access the admin dashboard.
  - From the dashboard, the admin can create subjects, add chapters, set up quizzes, and manage questions.
  
- **User:**
  - Users can register and then log in.
  - On logging in, users can choose a subject/chapter, start quizzes, and view past scores and performance analytics.

## Scheduled and Async Jobs

- **Daily Reminders:** 
  - A scheduled job sends daily reminders via Google Chat Webhooks, SMS, or email for inactive users or when new quizzes are available.
- **Monthly Activity Report:** 
  - On the first day of every month, a report (HTML or PDF) is generated and sent via email summarizing quiz attempts, scores, and rankings.
- **Async CSV Exports:** 
  - Both users and the admin can trigger asynchronous CSV exports for quiz details. Celery handles these batch jobs and alerts the user/admin upon completion.

## Contributing

Contributions are welcome! If you’d like to contribute, please:

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Add new feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request with a detailed description of your changes.

For any major changes, please open an issue first to discuss what you would like to change.

## Contact

For any questions, feedback, or issues, please reach out via:
- **Email:** 21f1001520@ds.study.iitm.ac.in
- **GitHub Issues:** [Quiz Master Issues](https://github.com/21f1001520/quiz_master_21f1001520/issues)
