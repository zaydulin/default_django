import smtplib
import ssl
from django.core.mail import get_connection, EmailMultiAlternatives
from django.conf import settings


class EmailService:
    """Сервис для отправки email с поддержкой SMTP настроек пользователя"""

    @staticmethod
    def test_smtp_connection(smtp_settings):
        """
        Тестирование SMTP подключения
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

                # Отправляем EHLO
                server.ehlo()

                if smtp_settings.email_use_tls:
                    print("   🔐 Запускаем STARTTLS...")
                    server.starttls(context=ssl.create_default_context())
                    server.ehlo()

            print("   🔑 Авторизуемся...")
            if smtp_settings.email_host_user and smtp_settings.email_host_password:
                server.login(smtp_settings.email_host_user, smtp_settings.email_host_password)
                print(f"   ✅ Авторизация успешна!")

            server.quit()
            print("   ✅ Тест подключения пройден успешно")
            return True, "Подключение успешно"

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"❌ Ошибка аутентификации: {str(e)}"
            print(error_msg)
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

        try:
            if smtp_settings:
                # Создаем кастомное соединение
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
                # Используем стандартные настройки
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=message,
                    from_email=from_email or settings.DEFAULT_FROM_EMAIL,
                    to=recipient_list
                )

            # Добавляем HTML версию
            if html_message:
                email.attach_alternative(html_message, "text/html")

            # Добавляем файлы
            if files:
                for file_path in files:
                    try:
                        with open(file_path, 'rb') as f:
                            email.attach(file_path.split('/')[-1], f.read())
                    except Exception as e:
                        print(f"❌ Ошибка прикрепления файла {file_path}: {str(e)}")

            # Отправляем
            email.send(fail_silently=False)
            print("✅ Email успешно отправлен!")
            return True, "Email успешно отправлен"

        except Exception as e:
            error_msg = f"❌ Ошибка отправки email: {str(e)}"
            print(error_msg)
            return False, error_msg