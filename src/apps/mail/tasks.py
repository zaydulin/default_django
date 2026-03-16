import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from .models import UserSettingsSMTP
from .services import EmailService

logger = logging.getLogger(__name__)


@shared_task
def check_all_smtp_settings():
    """
    Периодическая задача для проверки всех SMTP настроек каждые 30 минут
    """
    print("\n" + "=" * 60)
    print("🔍 [CELERY] Запуск проверки всех SMTP настроек")
    print("=" * 60)

    # Получаем все SMTP настройки
    smtp_settings_list = UserSettingsSMTP.objects.select_related('user').all()

    total = smtp_settings_list.count()
    working = 0
    failed = 0

    print(f"📊 Всего настроек для проверки: {total}")

    for smtp in smtp_settings_list:
        result = check_single_smtp_setting(smtp)

        if result['status'] == 'working':
            working += 1
        else:
            failed += 1

        # Логируем результат
        log_smtp_check_result(smtp, result)

    # Отправляем отчет администраторам (опционально)
    send_smtp_check_report.delay(total, working, failed)

    print("\n" + "=" * 60)
    print(f"📊 ИТОГИ ПРОВЕРКИ:")
    print(f"   ✅ Работает: {working}")
    print(f"   ❌ Не работает: {failed}")
    print(f"   📊 Всего: {total}")
    print("=" * 60 + "\n")

    return {
        'total': total,
        'working': working,
        'failed': failed,
        'timestamp': timezone.now().isoformat()
    }


def check_single_smtp_setting(smtp):
    """
    Проверка одного SMTP подключения с сохранением статуса
    """
    try:
        print(f"\n   📧 Проверка SMTP для пользователя: {smtp.user.username}")
        print(f"      Host: {smtp.email_host}")
        print(f"      Port: {smtp.email_port}")
        print(f"      User: {smtp.email_host_user}")

        # Обновляем счетчик проверок
        smtp.check_count += 1

        # Тестируем подключение
        success, message = EmailService.test_smtp_connection(smtp)

        # Обновляем время проверки
        smtp.last_check_time = timezone.now()

        if success:
            print(f"      ✅ УСПЕХ: {message}")
            smtp.last_check_success = True
            smtp.success_count += 1
            smtp.last_error = None
        else:
            print(f"      ❌ ОШИБКА: {message}")
            smtp.last_check_success = False
            smtp.failure_count += 1
            smtp.last_error = message

        smtp.save(update_fields=[
            'last_check_time', 'last_check_success', 'last_error',
            'check_count', 'success_count', 'failure_count'
        ])

        return {
            'status': 'working' if success else 'failed',
            'message': message,
            'user': smtp.user.username,
            'smtp_id': smtp.id
        }

    except Exception as e:
        error_msg = f"Критическая ошибка: {str(e)}"
        print(f"      ❌ {error_msg}")

        smtp.last_check_time = timezone.now()
        smtp.last_check_success = False
        smtp.failure_count += 1
        smtp.last_error = error_msg
        smtp.save()

        return {
            'status': 'error',
            'message': error_msg,
            'user': smtp.user.username if smtp.user else 'Unknown',
            'smtp_id': smtp.id
        }

def log_smtp_check_result(smtp, result):
    """
    Логирование результата проверки
    """
    from django.core.cache import cache

    # Сохраняем в кэш для быстрого доступа
    cache_key = f'smtp_status_{smtp.id}'
    cache.set(cache_key, result, timeout=3600)  # храним 1 час

    # Можно также сохранять в отдельную модель логов
    # SmtpCheckLog.objects.create(
    #     smtp_settings=smtp,
    #     status=result['status'],
    #     message=result['message']
    # )


@shared_task
def send_smtp_check_report(total, working, failed):
    """
    Отправка отчета о проверке SMTP администраторам
    """
    from django.core.mail import send_mail
    from django.contrib.auth import get_user_model
    from django.conf import settings

    User = get_user_model()

    # Получаем всех администраторов
    admins = User.objects.filter(is_superuser=True)

    if not admins:
        return "Нет администраторов для отправки отчета"

    subject = f"📊 Отчет о проверке SMTP настроек - {timezone.now().strftime('%d.%m.%Y %H:%M')}"

    message = f"""
    Результаты проверки SMTP настроек:

    ✅ Работает: {working}
    ❌ Не работает: {failed}
    📊 Всего проверено: {total}

    Детали можно посмотреть в логах.
    """

    for admin in admins:
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin.email],
                fail_silently=True,
            )
            print(f"   📧 Отчет отправлен администратору {admin.email}")
        except Exception as e:
            print(f"   ❌ Ошибка отправки отчета {admin.email}: {e}")

    return f"Отчет отправлен {admins.count()} администраторам"


@shared_task
def check_specific_smtp(smtp_id):
    """
    Проверка конкретного SMTP подключения по ID
    """
    try:
        smtp = UserSettingsSMTP.objects.get(id=smtp_id)
        result = check_single_smtp_setting(smtp)

        # Отправляем уведомление пользователю если проблема
        if result['status'] != 'working':
            notify_user_about_smtp_problem.delay(smtp.user.id, result)

        return result

    except UserSettingsSMTP.DoesNotExist:
        return {'status': 'error', 'message': f'SMTP с id {smtp_id} не найден'}


@shared_task
def notify_user_about_smtp_problem(user_id, result):
    """
    Уведомление пользователя о проблемах с SMTP
    """
    from django.core.mail import send_mail
    from django.contrib.auth import get_user_model
    from django.conf import settings

    User = get_user_model()

    try:
        user = User.objects.get(id=user_id)

        subject = "⚠️ Проблема с SMTP настройками"
        message = f"""
        Уважаемый {user.get_full_name() or user.username}!

        При проверке ваших SMTP настроек обнаружена проблема:

        ❌ {result['message']}

        Пожалуйста, проверьте настройки SMTP в личном кабинете.

        С уважением,
        Администрация сайта
        """

        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

        print(f"   📧 Уведомление отправлено пользователю {user.email}")

    except Exception as e:
        print(f"   ❌ Ошибка отправки уведомления: {e}")