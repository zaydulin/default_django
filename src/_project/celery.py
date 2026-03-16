import os
from celery import Celery
from celery.schedules import crontab

# Установите переменную окружения для настроек Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', '_project.settings')

app = Celery('demo')

# Используйте строку конфигурации для Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматически находите задачи в приложениях
app.autodiscover_tasks()

# Настройка расписания
app.conf.beat_schedule = {
    # Запуск check_mass_mail_campaigns каждую минуту
    'check-mass-mail-campaigns-every-minute': {
        'task': 'mail.tasks.run_check_mass_mail_campaigns',
        'schedule': crontab(minute='*'),  # Каждую минуту
        'options': {
            'expires': 60,  # Задача считается устаревшей через 60 секунд
        }
    },

    # Запуск check_mail каждые 5 минут
    'check-mail-every-5-minutes': {
        'task': 'mail.tasks.run_check_mail',
        'schedule': crontab(minute='*/5'),  # Каждые 5 минут
        'options': {
            'expires': 300,  # Задача считается устаревшей через 5 минут
        }
    },

    # Запуск обеих команд каждый час
    'both-checks-every-hour': {
        'task': 'mail.tasks.run_both_checks',
        'schedule': crontab(minute=0),  # Каждый час в 0 минут
        'options': {
            'expires': 3600,
        }
    },
}

# Для отладки можно добавить более частое расписание
if os.environ.get('DEBUG') == 'True':
    app.conf.beat_schedule.update({
        # Для тестирования - каждые 10 секунд
        'check-mass-mail-campaigns-test': {
            'task': 'mail.tasks.run_check_mass_mail_campaigns',
            'schedule': 10.0,  # Каждые 10 секунд
        },
        'check-mail-test': {
            'task': 'mail.tasks.run_check_mail',
            'schedule': 15.0,  # Каждые 15 секунд
        },
    })