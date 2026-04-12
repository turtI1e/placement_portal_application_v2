# Placement Portal V2

A modern placement portal with Flask API backend and Vue.js frontend.  
Features role-based access (Admin, Company, Student), Redis caching, Celery background jobs, and comprehensive placement management.

## Features
- JWT Authentication
- Admin: approve/reject companies and drives, manage users, view all applications
- Company: create drives, manage applications, shortlist students
- Student: view drives, apply, track status, export history as CSV
- Scheduled tasks: daily reminders, monthly reports
- Async CSV export
- Redis caching for performance

## Tech Stack
- Backend: Flask, SQLAlchemy, JWT, Celery, Redis
- Frontend: Vue 3, Vue Router, Vuex, Axios, Bootstrap 5
- Database: SQLite

## Setup Instructions

### Backend
```bash
cd backend
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env   # Edit with your credentials
python init_db.py
# Start Redis (if not running)
redis-server
# Start Celery worker (new terminal)
celery -A celery_app.celery worker --loglevel=info
# Start Celery beat (new terminal)
celery -A celery_app.celery beat --loglevel=info
# Start Flask
python app.py
