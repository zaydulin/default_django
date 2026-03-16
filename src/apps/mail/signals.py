import smtplib
import ssl
import base64
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives, get_connection
from django.template.loader import render_to_string
from django.conf import settings
from .models import Message, MassMailCampaign, MassMailLog, UserSettingsSMTP

# Включаем печать для отладки
DEBUG = True


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

        # Добавляем шапку если есть
        if smtp_settings and smtp_settings.message_header:
            full_message = smtp_settings.message_header + "\n\n" + full_message
            print("📌 Добавлена шапка сообщения")

        # Добавляем подвал если есть
        if smtp_settings and smtp_settings.message_footer:
            full_message = full_message + "\n\n" + smtp_settings.message_footer
            print("📌 Добавлен подвал сообщения")

        # Создаем HTML версию
        try:
            html_message = render_to_string('moderation/mail/email_template.html', {
                'message': message_obj.message,
                'subject': message_obj.subject,
                'header': smtp_settings.message_header if smtp_settings else None,
                'footer': smtp_settings.message_footer if smtp_settings else None,
                'user': message_obj.user,
            })
            print("✅ HTML шаблон создан успешно")
        except Exception as e:
            print(f"⚠️ Ошибка создания HTML шаблона: {str(e)}")
            html_message = None

        return full_message, html_message


@receiver(post_save, sender=Message)
def send_email_on_message_create(sender, instance, created, **kwargs):
    """
    Сигнал для отправки email при создании нового сообщения
    """
    # Отправляем только для новых сообщений, не черновиков и с получателями
    if (created and not instance.self_field and instance.clients):
        print("\n" + "=" * 60)
        print("🚀 СИГНАЛ: Новое сообщение создано")
        print("=" * 60)
        print(f"📧 ID сообщения: {instance.id}")
        print(f"👤 Отправитель: {instance.user.username} ({instance.user.email})")
        print(f"📋 Тема: {instance.subject}")

        try:
            # Получаем SMTP настройки отправителя
            print("\n🔍 Ищем SMTP настройки пользователя...")
            smtp_settings = UserSettingsSMTP.objects.filter(user=instance.user).first()

            if smtp_settings:
                print(f"✅ Найдены SMTP настройки:")
                print(f"   Host: {smtp_settings.email_host}")
                print(f"   Port: {smtp_settings.email_port}")
                print(f"   User: {smtp_settings.email_host_user}")
                print(f"   From: {smtp_settings.default_from_email}")

                # Проверяем логин для Beget
                if smtp_settings.email_host == 'smtp.beget.com':
                    if '@' not in smtp_settings.email_host_user:
                        print(f"   ⚠️ ВНИМАНИЕ: Для Beget логин должен быть полным email!")
                        print(f"      Будет автоматически исправлено на: {smtp_settings.default_from_email}")
            else:
                print("ℹ️ SMTP настройки не найдены")
                print("   Для отправки писем необходимо настроить SMTP в личном кабинете")
                return

            # Получаем список получателей
            recipients = instance.get_clients_list()
            print(f"\n👥 Получатели ({len(recipients)}): {recipients}")

            if not recipients:
                print("⚠️ Нет получателей, пропускаем отправку")
                return

            # Подготавливаем сообщение
            full_message, html_message = EmailService.prepare_message(instance, smtp_settings)

            # Определяем отправителя
            if smtp_settings and smtp_settings.default_from_email:
                from_email = smtp_settings.default_from_email
            else:
                from_email = instance.user.email

            # Получаем файлы
            files = None
            if instance.files.exists():
                files = [f.file.path for f in instance.files.all()]
                print(f"📎 Прикреплено файлов: {len(files)}")

            # Отправляем email
            success, result = EmailService.send_email(
                subject=instance.subject or "Новое сообщение",
                message=full_message,
                from_email=from_email,
                recipient_list=recipients,
                smtp_settings=smtp_settings,
                html_message=html_message,
                files=files
            )

            if success:
                print(f"\n✅ УСПЕХ: {result}")
            else:
                print(f"\n❌ ОШИБКА: {result}")

        except Exception as e:
            print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА В СИГНАЛЕ: {str(e)}")
            import traceback
            traceback.print_exc()

        print("=" * 60 + "\n")