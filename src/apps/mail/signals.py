import smtplib
import ssl
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from .models import Message
from django.utils.html import strip_tags
DEBUG = True

from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()

from django.contrib.auth import get_user_model
import logging

# Настройка логирования
logger = logging.getLogger(__name__)

User = get_user_model()

from django.contrib.auth import get_user_model

from django.contrib.auth import get_user_model
from .models import UserSettingsSMTP

import json
import random
import string
import requests
from urllib.parse import urlencode, quote
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender=User)
def create_user_mailbox_and_smtp_settings(sender, instance, created, **kwargs):
    if created:
        print("=" * 60)
        print(f"[DEBUG] Обработка сигнала для: {instance.username}")
        print("=" * 60)

        # Формируем данные
        mailbox_name = instance.email.split('@')[0] if instance.email else instance.username
        domain = "works-all.ru"
        full_email = f"{mailbox_name}@{domain}"

        random_password = ''.join(random.choices(
            string.ascii_letters + string.digits + "!@#$%^&*", k=16
        ))

        api_login = "a90212rd"
        api_password = "Samira0522"
        api_url = "https://api.beget.com/api/mail/createMailbox"

        input_data = {
            "domain": domain,
            "mailbox": mailbox_name,
            "mailbox_password": random_password
        }

        # 🔥 КЛЮЧЕВОЕ ИСПРАВЛЕНИЕ:
        # 1. JSON → строка
        input_data_json = json.dumps(input_data, ensure_ascii=False, separators=(',', ':'))
        # 2. URL-кодируем ВСЮ строку (safe='' — кодируем даже / и ?)
        input_data_encoded = quote(input_data_json, safe='')

        # 3. Простые параметры (их requests закодирует нормально)
        simple_params = {
            "login": api_login,
            "passwd": api_password,
            "input_format": "json",
            "output_format": "json",
        }

        # 4. Собираем базовый query string через urlencode
        base_query = urlencode(simple_params)

        # 5. Добавляем УЖЕ закодированный input_data БЕЗ повторного кодирования
        full_query = f"{base_query}&input_data={input_data_encoded}"

        # 6. Финальный URL
        full_url = f"{api_url}?{full_query}"

        mailbox_created = False
        real_error = None

        try:
            print(f"[DEBUG] Отправка запроса: {full_url[:200]}...")  # Обрезаем для лога

            # 🔥 Отправляем готовый URL, БЕЗ params!
            response = requests.get(full_url, timeout=30)

            print(f"[DEBUG] HTTP Status: {response.status_code}")
            print(f"[DEBUG] Response body: {response.text[:500]}")

            # Пробуем распарсить ответ
            try:
                result = response.json()
            except json.JSONDecodeError:
                print(f"[ERROR] Ответ не JSON: {response.text}")
                result = None

            # Проверка успешного ответа
            if response.status_code == 200 and result:
                if result.get('status') == 'success':
                    answer = result.get('answer', {})
                    if isinstance(answer, dict) and answer.get('status') == 'success':
                        print(f"[SUCCESS] ✅ Ящик {full_email} создан!")
                        mailbox_created = True
                    else:
                        errors = answer.get('errors', []) if isinstance(answer, dict) else []
                        if errors:
                            err = errors[0]
                            print(f"[ERROR] ❌ {err.get('error_code')}: {err.get('error_text')}")
                            real_error = err.get('error_text')
            else:
                print(f"[ERROR] ❌ Ошибка API: {result}")

        except requests.exceptions.RequestException as e:
            print(f"[ERROR] ❌ Сетевая ошибка: {e}")
            real_error = str(e)
        except Exception as e:
            print(f"[ERROR] ❌ Ошибка: {e}")
            real_error = str(e)

        # Логика создания SMTP-настроек (без изменений)
        if not mailbox_created:
            print(f"[WARNING] ⚠️ Ящик НЕ создан. Создайте вручную: {mailbox_name}@{domain}")

        try:
            UserSettingsSMTP.objects.create(
                user=instance,
                email_host="mail.works-all.ru",
                default_from_email=full_email,
                email_port=587,
                email_host_user=full_email,
                email_host_password=random_password,
                email_use_tls=True,
                email_use_ssl=False,
                message_header=f"Здравствуйте, {instance.get_full_name() or instance.username}!",
                message_footer="\n--\nС уважением, администрация сайта",
            )
            print(f"[SUCCESS] ✅ SMTP-настройки созданы")
        except Exception as e:
            print(f"[ERROR] ❌ Ошибка создания SMTP: {e}")

        print("=" * 60)

def debug_print(*args, **kwargs):
    if DEBUG:
        print("🔍 [SMTP DEBUG]", *args, **kwargs)


class EmailService:
    """Сервис для отправки email с поддержкой SMTP настроек пользователя"""

    @staticmethod
    def fix_smtp_settings(smtp_settings, from_email=None):
        """
        Исправляет SMTP настройки для разных провайдеров
        """
        if not smtp_settings:
            return smtp_settings

        # Для Beget.com
        if smtp_settings.email_host == 'smtp.beget.com':
            print("   📌 Обнаружен Beget SMTP, применяем коррекцию")

            # Логин должен быть полным email
            if '@' not in smtp_settings.email_host_user:
                # Используем from_email или default_from_email
                correct_login = from_email or smtp_settings.default_from_email
                if correct_login and '@' in correct_login:
                    print(f"   🔧 Исправляем логин: '{smtp_settings.email_host_user}' -> '{correct_login}'")
                    smtp_settings.email_host_user = correct_login
                else:
                    print(f"   ⚠️ Не могу исправить логин, нет правильного email")

            # Для Beget порт должен быть 2525
            if smtp_settings.email_port != '2525':
                print(f"   🔧 Исправляем порт: {smtp_settings.email_port} -> 2525")
                smtp_settings.email_port = '2525'

        return smtp_settings

    @staticmethod
    def test_smtp_connection(smtp_settings):
        """
        Тестирование SMTP подключения перед отправкой
        """
        try:
            print(f"\n📧 Тестируем SMTP подключение:")
            print(f"   Host: {smtp_settings.email_host}")
            print(f"   Port: {smtp_settings.email_port}")
            print(f"   User: {smtp_settings.email_host_user}")
            print(f"   TLS: {smtp_settings.email_use_tls}")
            print(f"   SSL: {smtp_settings.email_use_ssl}")

            # Создаем соединение
            if smtp_settings.email_use_ssl:
                context = ssl.create_default_context()
                server = smtplib.SMTP_SSL(
                    smtp_settings.email_host,
                    int(smtp_settings.email_port) if smtp_settings.email_port else 465,
                    context=context,
                    timeout=30
                )
            else:
                server = smtplib.SMTP(
                    smtp_settings.email_host,
                    int(smtp_settings.email_port) if smtp_settings.email_port else 587,
                    timeout=30
                )
                server.set_debuglevel(2)
                print("   🔌 Соединение установлено")

                # Отправляем EHLO
                server.ehlo()

                if smtp_settings.email_use_tls:
                    print("   🔐 Запускаем STARTTLS...")
                    server.starttls(context=ssl.create_default_context())
                    server.ehlo()

            print("   🔑 Авторизуемся...")
            if smtp_settings.email_host_user and smtp_settings.email_host_password:
                # Для отладки покажем первые символы пароля
                pwd_preview = smtp_settings.email_host_password[:4] + '...' if len(
                    smtp_settings.email_host_password) > 4 else '***'
                print(f"   Пароль (первые символы): {pwd_preview}")

                login_result = server.login(smtp_settings.email_host_user, smtp_settings.email_host_password)
                print(f"   ✅ Авторизация успешна!")

            server.quit()
            print("   ✅ Тест подключения пройден успешно")
            return True, "Подключение успешно"

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"❌ Ошибка аутентификации: {str(e)}"
            print(error_msg)
            print("\n💡 Возможные причины:")
            print("   1. Неправильный логин или пароль")
            print(f"      Логин: {smtp_settings.email_host_user}")
            print("   2. Для Beget логин должен быть полным email адресом (user@domain.ru)")
            print("   3. Пароль от почтового ящика, а не от аккаунта хостинга")
            print("   4. Не включен доступ по SMTP в панели управления хостинга")
            return False, error_msg
        except Exception as e:
            error_msg = f"❌ Ошибка подключения: {str(e)}"
            print(error_msg)
            return False, error_msg

    @staticmethod
    def send_email(subject, message, from_email, recipient_list,
                   smtp_settings=None, html_message=None, files=None):
        """
        Отправка email с использованием указанных SMTP настроек
        """
        print(f"\n📨 Отправка email:")
        print(f"   Тема: {subject}")
        print(f"   От: {from_email}")
        print(f"   Кому: {recipient_list}")
        print(f"   Используем кастомные SMTP: {bool(smtp_settings)}")

        # Исправляем настройки если нужно
        if smtp_settings:
            smtp_settings = EmailService.fix_smtp_settings(smtp_settings, from_email)

        try:
            # Проверяем SMTP настройки перед отправкой
            if smtp_settings:
                print("🔍 Проверяем SMTP настройки...")
                success, error_msg = EmailService.test_smtp_connection(smtp_settings)
                if not success:
                    print(f"⚠️ SMTP проверка не пройдена: {error_msg}")
                    print("❌ Отмена отправки")
                    return False, error_msg

                # Создаем email с кастомными настройками
                print("📧 Создаем email с кастомными настройками...")

                # Для Django >= 3.2 используем get_connection
                if smtp_settings.email_use_ssl:
                    connection = get_connection(
                        backend='django.core.mail.backends.smtp.EmailBackend',
                        host=smtp_settings.email_host,
                        port=int(smtp_settings.email_port) if smtp_settings.email_port else 465,
                        username=smtp_settings.email_host_user,
                        password=smtp_settings.email_host_password,
                        use_tls=False,
                        use_ssl=True,
                        timeout=30,
                    )
                else:
                    connection = get_connection(
                        backend='django.core.mail.backends.smtp.EmailBackend',
                        host=smtp_settings.email_host,
                        port=int(smtp_settings.email_port) if smtp_settings.email_port else 587,
                        username=smtp_settings.email_host_user,
                        password=smtp_settings.email_host_password,
                        use_tls=smtp_settings.email_use_tls,
                        use_ssl=False,
                        timeout=30,
                    )

                email = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=from_email,
                    to=recipient_list,
                    connection=connection
                )
            else:
                print("ℹ️ Используем стандартные настройки Django")
                print(f"   EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', 'не задан')}")
                print(f"   EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', 'не задан')}")

                # Проверяем наличие настроек в settings.py
                if not hasattr(settings, 'EMAIL_HOST') or settings.EMAIL_HOST == 'localhost':
                    print("   ⚠️ Стандартные настройки SMTP не настроены в settings.py")
                    print("   ❌ Отмена отправки")
                    return False, "SMTP не настроен в settings.py"

                email = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                    to=recipient_list
                )

            # Добавляем HTML версию если есть
            if html_message:
                email.attach_alternative(html_message, "text/html")
                print("📄 Добавлена HTML версия")

            # Добавляем файлы если есть
            if files:
                for file_path in files:
                    try:
                        with open(file_path, 'rb') as f:
                            email.attach(file_path.split('/')[-1], f.read())
                        print(f"📎 Прикреплен файл: {file_path}")
                    except Exception as e:
                        print(f"❌ Ошибка прикрепления файла {file_path}: {str(e)}")

            # Отправляем
            print("📤 Отправляем...")
            email.send(fail_silently=False)
            print("✅ Email успешно отправлен!")
            return True, "Email успешно отправлен"

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"❌ Ошибка аутентификации SMTP: {str(e)}"
            print(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"❌ Ошибка отправки email: {str(e)}"
            print(error_msg)
            return False, error_msg

    @staticmethod
    def prepare_message(message_obj, smtp_settings=None):
        """
        Подготовка сообщения с учетом шапки и подвала
        """
        full_message = message_obj.message
        print(f"\n📝 Подготовка сообщения ID: {message_obj.id}")

        # Выводим шапку и подвал для отладки
        if smtp_settings:
            print(f"   📌 SMTP Settings found for user: {smtp_settings.user.username}")
            print(f"   📌 Header present: {bool(smtp_settings.message_header)}")
            print(f"   📌 Footer present: {bool(smtp_settings.message_footer)}")

            if smtp_settings.message_header:
                print(f"   📌 Header content: {smtp_settings.message_header[:50]}...")
            if smtp_settings.message_footer:
                print(f"   📌 Footer content: {smtp_settings.message_footer[:50]}...")
        else:
            print("   ℹ️ No SMTP settings found")

        # Добавляем шапку если есть
        if smtp_settings and smtp_settings.message_header:
            full_message = smtp_settings.message_header + "\n\n" + full_message
            print("   ✅ Шапка добавлена в текстовую версию")

        # Добавляем подвал если есть
        if smtp_settings and smtp_settings.message_footer:
            full_message = full_message + "\n\n" + smtp_settings.message_footer
            print("   ✅ Подвал добавлен в текстовую версию")

        # Создаем HTML версию
        try:
            context = {
                'message': message_obj.message,
                'subject': message_obj.subject,
                'user': message_obj.user,
            }

            # Добавляем header и footer в контекст, если они есть
            if smtp_settings:
                context['header'] = smtp_settings.message_header
                context['footer'] = smtp_settings.message_footer
                print(f"   📌 Header in context: {bool(context.get('header'))}")
                print(f"   📌 Footer in context: {bool(context.get('footer'))}")

            html_message = render_to_string('moderation/mail/email_template.html', context)
            print("✅ HTML шаблон создан успешно")
            print(f"   📄 HTML template path: moderation/mail/email_template.html")

        except Exception as e:
            print(f"⚠️ Ошибка создания HTML шаблона: {str(e)}")
            import traceback
            traceback.print_exc()
            html_message = None

        return full_message, html_message


@receiver(post_save, sender=Message)
def send_email_on_message_create(sender, instance, created, **kwargs):
    """
    Сигнал для отправки email при создании нового сообщения
    """

    # Отправляем только для новых сообщений
    if created and not instance.self_field and instance.clients:

        print("\n" + "=" * 60)
        print("🚀 СИГНАЛ: Новое сообщение создано")
        print("=" * 60)

        print(f"📧 ID сообщения: {instance.id}")
        print(f"👤 Отправитель: {instance.user.username} ({instance.user.email})")
        print(f"📋 Тема: {instance.subject}")

        try:

            # -------------------------------------------------------
            # SMTP НАСТРОЙКИ
            # -------------------------------------------------------

            print("\n🔍 Ищем SMTP настройки пользователя...")
            smtp_settings = UserSettingsSMTP.objects.filter(user=instance.user).first()

            if smtp_settings:
                print("✅ Найдены SMTP настройки")
                print(f"Host: {smtp_settings.email_host}")
                print(f"Port: {smtp_settings.email_port}")
                print(f"User: {smtp_settings.email_host_user}")
                print(f"From: {smtp_settings.default_from_email}")
            else:
                print("❌ SMTP настройки не найдены")
                return

            # -------------------------------------------------------
            # ПОЛУЧАТЕЛИ
            # -------------------------------------------------------

            recipients = instance.get_clients_list()

            print(f"\n👥 Получатели ({len(recipients)}):")
            print(recipients)

            if not recipients:
                print("⚠️ Нет получателей")
                return

            # -------------------------------------------------------
            # ПОДГОТОВКА ПИСЬМА
            # -------------------------------------------------------

            print("\n📝 Подготавливаем письмо...")

            full_message, html_message = EmailService.prepare_message(
                instance,
                smtp_settings
            )

            # Если HTML есть — делаем текстовую версию
            if html_message:
                text_message = strip_tags(html_message)
            else:
                text_message = full_message

            # -------------------------------------------------------
            # ОТПРАВИТЕЛЬ
            # -------------------------------------------------------

            if smtp_settings.default_from_email:
                from_email = smtp_settings.default_from_email
            else:
                from_email = instance.user.email

            print(f"\n📤 Отправитель: {from_email}")

            # -------------------------------------------------------
            # ФАЙЛЫ
            # -------------------------------------------------------

            files = None

            if instance.files.exists():
                files = [f.file.path for f in instance.files.all()]
                print(f"📎 Прикреплено файлов: {len(files)}")

            # -------------------------------------------------------
            # ОТПРАВКА
            # -------------------------------------------------------

            success, result = EmailService.send_email(
                subject=instance.subject or "Новое сообщение",
                message=text_message,       # текстовая версия
                from_email=from_email,
                recipient_list=recipients,
                smtp_settings=smtp_settings,
                html_message=html_message,  # HTML версия
                files=files
            )

            if success:
                print("\n✅ Email успешно отправлен")
            else:
                print("\n❌ Ошибка отправки:")
                print(result)

        except Exception as e:
            print("\n❌ КРИТИЧЕСКАЯ ОШИБКА")
            print(str(e))

            import traceback
            traceback.print_exc()

        print("=" * 60 + "\n")
