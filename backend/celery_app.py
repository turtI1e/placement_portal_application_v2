from celery import Celery
from celery.schedules import crontab
from config import Config

def make_celery():
    celery = Celery(
        __name__,
        broker=Config.CELERY_BROKER_URL,
        backend=Config.CELERY_RESULT_BACKEND
    )
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='UTC',
        enable_utc=True,
        # Explicitly list task modules to import
        imports=(
        'tasks.daily_reminder',
        'tasks.monthly_report',
        'tasks.export_csv'
        ),
        beat_schedule={
            'daily-reminder': {
                'task': 'tasks.daily_reminder.send_daily_reminders',
                'schedule': crontab(hour=8, minute=0),  # 8 AM daily
            },
            'monthly-report': {
                'task': 'tasks.monthly_report.generate_monthly_report',
                'schedule': crontab(minute=0, hour=0, day_of_month=1),  # 1st of each month
            }
        }
    )
    return celery

celery = make_celery()
