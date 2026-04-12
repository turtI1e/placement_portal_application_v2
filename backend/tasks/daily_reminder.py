from celery_app import celery
from models import Drive, Student, Application
from utils.email import send_email
from utils.webhook import send_google_chat_message
from datetime import date, timedelta
from app import create_app
import os
from sqlalchemy import select

def parse_eligibility(eligibility_str):
    criteria = {}
    if not eligibility_str:
        return criteria
    parts = [p.strip() for p in eligibility_str.split(';') if p.strip()]
    for part in parts:
        if ':' in part:
            key, value = part.split(':', 1)
            key = key.strip().lower()
            value = value.strip()
            if key == 'branch':
                criteria['branches'] = [b.strip().lower() for b in value.split(',')]
            elif key == 'min_cgpa':
                try:
                    criteria['min_cgpa'] = float(value)
                except ValueError:
                    pass
            elif key == 'year':
                criteria['years'] = [int(y.strip()) for y in value.split(',') if y.strip().isdigit()]
    return criteria

def is_student_eligible(student, criteria):
    if not criteria:
        return True
    if 'branches' in criteria and student.branch:
        if student.branch.lower() not in criteria['branches']:
            return False
    if 'min_cgpa' in criteria and student.cgpa is not None:
        if student.cgpa < criteria['min_cgpa']:
            return False
    if 'years' in criteria and student.year is not None:
        if student.year not in criteria['years']:
            return False
    return True

@celery.task
def send_daily_reminders():
    app = create_app()
    with app.app_context():
        upcoming_deadline = date.today() + timedelta(days=3)
        drives = Drive.query.filter(Drive.deadline <= upcoming_deadline, Drive.status == 'approved').all()
        
        reminders_sent = 0
        for drive in drives:
            criteria = parse_eligibility(drive.eligibility)

            subq = select(Application.student_id).where(
                Application.drive_id == drive.id
            ).subquery()
            eligible_students = Student.query.filter(~Student.user_id.in_(subq)).all()
            
            for student in eligible_students:
                if not is_student_eligible(student, criteria):
                    continue
                subject = f"Reminder: {drive.job_title} deadline approaching"
                body = f"<p>Dear {student.name},</p><p>The placement drive '{drive.job_title}' by {drive.company.company_name} has deadline on {drive.deadline}. Apply soon!</p>"
                if send_email(student.user.email, subject, body):
                    reminders_sent += 1
        
        webhook_url = os.environ.get('GOOGLE_CHAT_WEBHOOK')
        if webhook_url and drives:
            message = f"Daily reminder sent for {len(drives)} drives ({reminders_sent} emails)."
            send_google_chat_message(webhook_url, message)
        
        return f"Reminders sent for {len(drives)} drives"
