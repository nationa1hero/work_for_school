import os
from celery import Celery
from celery.schedules import crontab

# Установка модуля настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'School_Diplom.settings.dev')

app = Celery('School_Diplom')

# Загрузка конфигурации Django в Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.beat_schedule = {
    'assign-tasks-every-week': {
        'task': 'backend.utils.assign_tasks_to_students',
        'schedule': crontab(0, 0, day_of_week='mon'),  # Каждый понедельник в полночь
    },
}

# Автоматическое обнаружение задач в приложениях Django
app.autodiscover_tasks()


@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
