from celery_app import celery
from models import Drive, Application
from utils.email import send_email
from datetime import date, timedelta
from app import create_app

@celery.task
def generate_monthly_report():
    app = create_app()
    with app.app_context():
        # Get previous month
        today = date.today()
        first_day_of_current_month = date(today.year, today.month, 1)
        last_day_of_prev_month = first_day_of_current_month - timedelta(days=1)
        year = last_day_of_prev_month.year
        month = last_day_of_prev_month.month
        first_day_of_prev_month = date(year, month, 1)
        
        # Query drives created in that month
        drives = Drive.query.filter(Drive.created_at >= first_day_of_prev_month,
                                     Drive.created_at <= last_day_of_prev_month).all()
        
        total_drives = len(drives)
        total_applications = Application.query.filter(Application.application_date >= first_day_of_prev_month,
                                                       Application.application_date <= last_day_of_prev_month).count()
        selected = Application.query.filter(Application.status == 'selected',
                                            Application.application_date >= first_day_of_prev_month,
                                            Application.application_date <= last_day_of_prev_month).count()
        
        # Generate HTML
        html = f"""
        <h2>Monthly Placement Report - {month}/{year}</h2>
        <p>Total Drives Conducted: {total_drives}</p>
        <p>Total Applications Received: {total_applications}</p>
        <p>Total Students Selected: {selected}</p>
        <h3>Drives Details:</h3>
        <ul>
        """
        for d in drives:
            html += f"<li>{d.job_title} by {d.company.company_name} - Applications: {d.applications.count()}</li>"
        html += "</ul>"
        
        # Send email to admin
        from config import Config
        admin_email = Config.ADMIN_EMAIL
        send_email(admin_email, f"Monthly Placement Report - {month}/{year}", html)
        
        return f"Monthly report for {month}/{year} sent"
