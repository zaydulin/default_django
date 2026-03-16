# apps/mail/tasks.py

from celery import shared_task
from django.core.management import call_command
from django.utils import timezone
import logging
from io import StringIO
import sys

logger = logging.getLogger(__name__)


@shared_task
def run_check_mass_mail_campaigns():
    """
    Задача для запуска команды check_mass_mail_campaigns
    """
    logger.info(f"Starting check_mass_mail_campaigns task at {timezone.now()}")

    # Перехватываем вывод команды
    stdout = StringIO()
    stderr = StringIO()

    try:
        # Запускаем команду
        call_command(
            'check_mass_mail_campaigns',
            stdout=stdout,
            stderr=stderr
        )

        # Логируем результат
        output = stdout.getvalue()
        error = stderr.getvalue()

        if output:
            logger.info(f"Command output: {output}")
        if error:
            logger.error(f"Command error: {error}")

        logger.info(f"Completed check_mass_mail_campaigns task at {timezone.now()}")

        return {
            'status': 'success',
            'output': output,
            'error': error,
            'timestamp': str(timezone.now())
        }

    except Exception as e:
        logger.exception(f"Error in check_mass_mail_campaigns task: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': str(timezone.now())
        }


@shared_task
def run_check_mail():
    """
    Задача для запуска команды check_mail
    """
    logger.info(f"Starting check_mail task at {timezone.now()}")

    # Перехватываем вывод команды
    stdout = StringIO()
    stderr = StringIO()

    try:
        # Запускаем команду
        call_command(
            'check_mail',
            stdout=stdout,
            stderr=stderr
        )

        # Логируем результат
        output = stdout.getvalue()
        error = stderr.getvalue()

        if output:
            logger.info(f"Command output: {output}")
        if error:
            logger.error(f"Command error: {error}")

        logger.info(f"Completed check_mail task at {timezone.now()}")

        return {
            'status': 'success',
            'output': output,
            'error': error,
            'timestamp': str(timezone.now())
        }

    except Exception as e:
        logger.exception(f"Error in check_mail task: {str(e)}")
        return {
            'status': 'error',
            'error': str(e),
            'timestamp': str(timezone.now())
        }


@shared_task
def run_both_checks():
    """
    Задача для последовательного запуска обеих команд
    """
    logger.info(f"Starting both checks task at {timezone.now()}")

    results = {}

    # Запускаем первую команду
    try:
        results['check_mass_mail_campaigns'] = run_check_mass_mail_campaigns()
    except Exception as e:
        results['check_mass_mail_campaigns'] = {'status': 'error', 'error': str(e)}

    # Запускаем вторую команду
    try:
        results['check_mail'] = run_check_mail()
    except Exception as e:
        results['check_mail'] = {'status': 'error', 'error': str(e)}

    logger.info(f"Completed both checks task at {timezone.now()}")

    return results