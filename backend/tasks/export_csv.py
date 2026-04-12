from celery_app import celery
from models import Student, Application
from app import create_app
import csv
import io

@celery.task(bind=True)
def export_applications_csv(self, student_id):
    # Convert student_id to int (it comes as string from JWT)
    try:
        student_id = int(student_id)
    except (TypeError, ValueError):
        return {'error': 'Invalid student ID'}

    app = create_app(skip_jwt=True)
    with app.app_context():
        student = Student.query.get(student_id)
        if not student:
            return {'error': 'Student not found'}

        applications = Application.query.filter_by(student_id=student_id).all()

        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Student ID', 'Student Name', 'Company', 'Job Title', 'Applied On', 'Deadline', 'Status'])
        for appl in applications:
            writer.writerow([
                student.user_id,
                student.name,
                appl.drive.company.company_name,
                appl.drive.job_title,
                appl.application_date.strftime('%Y-%m-%d'),
                appl.drive.deadline.strftime('%Y-%m-%d'),
                appl.status
            ])

        csv_content = output.getvalue()
        output.close()

        return {
            'student_name': student.name,
            'csv': csv_content,
            'filename': f"{student.name}_applications.csv"
        }
