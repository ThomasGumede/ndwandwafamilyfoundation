from celery.schedules import crontab

CELERY_BROKER_URL = f"redis://localhost:6379"
BROKER_URL = f"redis://localhost:6379"
CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_RESULT_EXTENDED = True
CELERY_worker_state_db = True
CELERY_result_persistent=True
CELERY_RESULT_BACKEND = 'django-db'
CELERY_TIMEZONE = 'Africa/Johannesburg'
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers.DatabaseScheduler'


CELERY_BEAT_SCHEDULE = {
    
    # 'send-email-update': {
    #     'task': 'home.tasks.send_update_email',
    #     'schedule': crontab(hour=9, minute=0),  # Run the task 23 hours
    # },
    'close-expired-events': {
        'task': 'events.tasks.check_events_status',
        'schedule': crontab(hour=9, minute=0)
    },
    'close-expired-campaigns': {
        'task': 'campaigns.tasks.check_campaigns_status',
        'schedule': crontab(hour=9, minute=0)
    },
}