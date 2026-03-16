from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth import get_user_model
from mail.models import UserSettingsSMTP, Message, SmtpCheckLog
import imaplib
import email
from email.header import decode_header
from datetime import datetime, timedelta
import re
import logging
import traceback

logger = logging.getLogger(__name__)
User = get_user_model()


class Command(BaseCommand):
    help = 'Проверка входящих писем для всех пользователей с SMTP настройками'

    def add_arguments(self, parser):
        parser.add_argument(
            '--minutes',
            type=int,
            default=30,
            help='Проверка писем за последние N минут (по умолчанию: 30)'
        )
        parser.add_argument(
            '--user',
            type=str,
            help='Проверить только конкретного пользователя (username)'
        )
        parser.add_argument(
            '--no-save',
            action='store_true',
            help='Не сохранять в БД (только просмотр)'
        )
        parser.add_argument(
            '--debug',
            action='store_true',
            help='Включить отладочный вывод IMAP'
        )
        parser.add_argument(
            '--check-smtp',
            action='store_true',
            help='Проверить только SMTP подключения (без проверки писем)'
        )

    def handle(self, *args, **options):
        minutes = options['minutes']
        username = options['user']
        no_save = options['no_save']
        debug = options['debug']
        check_smtp_only = options['check_smtp']

        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS('🔍 ПРОВЕРКА ПОЧТОВЫХ НАСТРОЕК'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

        # Получаем пользователей с SMTP настройками
        if username:
            try:
                user = User.objects.get(username=username)
                smtp_users = UserSettingsSMTP.objects.filter(user=user)
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Пользователь {username} не найден'))
                return
        else:
            smtp_users = UserSettingsSMTP.objects.select_related('user').all()

        if not smtp_users:
            self.stdout.write(self.style.WARNING('❌ Нет пользователей с SMTP настройками'))
            return

        self.stdout.write(self.style.SUCCESS(f'📊 Найдено пользователей: {smtp_users.count()}'))

        total_messages = 0
        total_saved = 0
        smtp_success = 0
        smtp_failed = 0

        for user_smtp in smtp_users:
            if check_smtp_only:
                # Только проверка SMTP подключения
                result = self.check_smtp_connection(user_smtp, debug)
                if result['success']:
                    smtp_success += 1
                else:
                    smtp_failed += 1
            else:
                # Полная проверка писем
                result = self.check_user_inbox(
                    user_smtp,
                    minutes=minutes,
                    save_to_db=not no_save,
                    debug=debug
                )
                total_messages += result['found']
                total_saved += result['saved']
                if result['smtp_success']:
                    smtp_success += 1
                else:
                    smtp_failed += 1

            self.stdout.write('-' * 60)

        self.stdout.write(self.style.SUCCESS('=' * 70))
        self.stdout.write(self.style.SUCCESS(f'📊 ИТОГО:'))
        if not check_smtp_only:
            self.stdout.write(self.style.SUCCESS(f'   Найдено писем: {total_messages}'))
            self.stdout.write(self.style.SUCCESS(f'   Сохранено: {total_saved}'))
        self.stdout.write(self.style.SUCCESS(f'   SMTP успешно: {smtp_success}'))
        self.stdout.write(self.style.SUCCESS(f'   SMTP ошибок: {smtp_failed}'))
        self.stdout.write(self.style.SUCCESS('=' * 70))

    def check_smtp_connection(self, user_smtp, debug=False):
        """Проверяет только SMTP/IMAP подключение и создает лог"""
        self.stdout.write(f"\n{'=' * 60}")
        self.stdout.write(f"👤 Проверка SMTP: {user_smtp.user.username} ({user_smtp.user.email})")
        self.stdout.write(f"{'=' * 60}")

        # Определяем IMAP сервер
        if user_smtp.email_host:
            imap_host = user_smtp.email_host.replace('smtp', 'imap')
        else:
            imap_host = 'imap.beget.com'

        imap_port = 993
        email_login = user_smtp.email_host_user
        email_password = user_smtp.email_host_password

        if not email_login or not email_password:
            self.log_smtp_check(
                user_smtp,
                False,
                "Нет учетных данных"
            )
            return {'success': False, 'error': 'Нет учетных данных'}

        self.stdout.write(f"📧 IMAP: {imap_host}:{imap_port}")
        self.stdout.write(f"📧 Логин: {email_login}")

        try:
            # Подключаемся к IMAP
            self.stdout.write("🔄 Подключение...")
            mail = imaplib.IMAP4_SSL(imap_host, imap_port, timeout=30)
            if debug:
                mail.debug = 4

            mail.login(email_login, email_password)
            self.stdout.write(self.style.SUCCESS("✅ Подключение успешно"))

            # Проверяем, что можем открыть INBOX
            mail.select("inbox")
            mail.logout()

            # Логируем успех
            self.log_smtp_check(
                user_smtp,
                True,
                f"Успешное подключение к {imap_host}"
            )

            return {'success': True, 'error': None}

        except imaplib.IMAP4.error as e:
            error_msg = f"Ошибка IMAP: {e}"
            self.stderr.write(self.style.ERROR(f"❌ {error_msg}"))

            # Логируем ошибку
            self.log_smtp_check(
                user_smtp,
                False,
                error_msg
            )

            return {'success': False, 'error': error_msg}

        except Exception as e:
            error_msg = f"Ошибка: {e}"
            self.stderr.write(self.style.ERROR(f"❌ {error_msg}"))

            # Логируем ошибку
            self.log_smtp_check(
                user_smtp,
                False,
                error_msg,
                traceback.format_exc()
            )

            return {'success': False, 'error': error_msg}

    def log_smtp_check(self, user_smtp, success, message, detailed_error=None):
        """Создает запись в логе проверок SMTP"""
        try:
            log_entry = SmtpCheckLog.objects.create(
                smtp_settings=user_smtp,
                status='success' if success else 'failed',
                message=message[:255]  # обрезаем до длины поля
            )

            # Обновляем статистику в UserSettingsSMTP
            user_smtp.last_check_time = timezone.now()
            user_smtp.last_check_success = success
            user_smtp.check_count = (user_smtp.check_count or 0) + 1

            if success:
                user_smtp.success_count = (user_smtp.success_count or 0) + 1
                user_smtp.last_error = None
            else:
                user_smtp.failure_count = (user_smtp.failure_count or 0) + 1
                user_smtp.last_error = message[:255]

            user_smtp.save(update_fields=[
                'last_check_time', 'last_check_success',
                'check_count', 'success_count', 'failure_count', 'last_error'
            ])

            self.stdout.write(f"   📝 Лог сохранен: {log_entry.status} - {log_entry.checked_at}")

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Ошибка сохранения лога: {e}"))

    def decode_mime_words(self, s):
        """Декодирует заголовки письма"""
        if not s:
            return ""
        try:
            decoded_parts = decode_header(s)
            result = ""
            for part, encoding in decoded_parts:
                if isinstance(part, bytes):
                    if encoding:
                        result += part.decode(encoding, errors='replace')
                    else:
                        result += part.decode('utf-8', errors='replace')
                else:
                    result += part
            return result
        except Exception as e:
            self.stderr.write(f"Ошибка декодирования: {e}")
            return str(s)

    def get_email_body(self, msg):
        """Извлекает тело письма"""
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                if content_type == "text/plain":
                    try:
                        payload = part.get_payload(decode=True)
                        charset = part.get_content_charset() or 'utf-8'
                        body += payload.decode(charset, errors='replace')
                        break
                    except:
                        continue
        else:
            try:
                payload = msg.get_payload(decode=True)
                charset = msg.get_content_charset() or 'utf-8'
                body = payload.decode(charset, errors='replace')
            except:
                body = str(msg.get_payload())
        return body.strip()

    def extract_email_from_string(self, email_string):
        """Извлекает email из строки вида 'Name <email@domain.com>'"""
        if not email_string:
            return ""
        match = re.search(r'<(.+?)>', email_string)
        if match:
            return match.group(1)
        return email_string.strip()

    def check_user_inbox(self, user_smtp, minutes=30, save_to_db=True, debug=False):
        """Проверяет входящие письма для конкретного пользователя"""
        self.stdout.write(f"\n{'=' * 60}")
        self.stdout.write(f"👤 Пользователь: {user_smtp.user.username} ({user_smtp.user.email})")
        self.stdout.write(f"{'=' * 60}")

        # Сначала проверяем SMTP подключение
        smtp_check = self.check_smtp_connection(user_smtp, debug)

        if not smtp_check['success']:
            return {'found': 0, 'saved': 0, 'smtp_success': False}

        # Определяем IMAP сервер
        if user_smtp.email_host:
            imap_host = user_smtp.email_host.replace('smtp', 'imap')
        else:
            imap_host = 'imap.beget.com'

        imap_port = 993
        email_login = user_smtp.email_host_user
        email_password = user_smtp.email_host_password
        email_address = user_smtp.default_from_email

        try:
            # Подключаемся к IMAP
            self.stdout.write("🔄 Подключение к IMAP для чтения писем...")
            mail = imaplib.IMAP4_SSL(imap_host, imap_port, timeout=30)
            if debug:
                mail.debug = 4

            mail.login(email_login, email_password)
            mail.select("inbox")

            # Ищем письма за последние N минут
            since_time = datetime.now() - timedelta(minutes=minutes)
            since_str = since_time.strftime("%d-%b-%Y")

            self.stdout.write(f"🔍 Поиск писем с {since_str}...")
            result, data = mail.search(None, f'(SINCE "{since_str}")')
            mail_ids = data[0].split()

            self.stdout.write(f"📊 Найдено писем: {len(mail_ids)}")

            found_count = len(mail_ids)
            saved_count = 0

            # Получаем последнюю дату проверки из логов
            last_log = SmtpCheckLog.objects.filter(
                smtp_settings=user_smtp,
                status='success'
            ).order_by('-checked_at').first()

            if last_log:
                self.stdout.write(f"📅 Последняя успешная проверка: {last_log.checked_at}")

            for i, mail_id in enumerate(mail_ids, 1):
                try:
                    mail_id_str = mail_id.decode() if isinstance(mail_id, bytes) else str(mail_id)

                    # Получаем письмо
                    result, msg_data = mail.fetch(mail_id, "(RFC822)")
                    msg = email.message_from_bytes(msg_data[0][1])

                    # Получаем дату письма
                    date_str = msg.get("Date", "")
                    try:
                        # Парсим дату письма
                        email_date = email.utils.parsedate_to_datetime(date_str)
                        # Приводим к локальному времени
                        email_date = timezone.make_aware(email_date) if timezone.is_naive(email_date) else email_date
                    except:
                        email_date = timezone.now()

                    # Декодируем заголовки
                    subject = self.decode_mime_words(msg.get("Subject", "Без темы"))
                    from_addr = self.decode_mime_words(msg.get("From", "Неизвестно"))
                    body = self.get_email_body(msg)

                    # Извлекаем email отправителя
                    sender_email = self.extract_email_from_string(from_addr)

                    self.stdout.write(f"\n{i}. 📨 {subject}")
                    self.stdout.write(f"   От: {from_addr}")
                    self.stdout.write(f"   Дата: {date_str}")

                    # Сохраняем в БД
                    if save_to_db:
                        if self.save_message_to_db(
                                user=user_smtp.user,
                                from_email=sender_email,
                                subject=subject,
                                body=body,
                                imap_id=mail_id_str,
                                received_date=email_date
                        ):
                            saved_count += 1

                except Exception as e:
                    self.stderr.write(self.style.ERROR(f"   ❌ Ошибка обработки письма {i}: {e}"))

            self.stdout.write(f"\n📊 Сохранено: {saved_count}")
            mail.logout()

            return {'found': found_count, 'saved': saved_count, 'smtp_success': True}

        except imaplib.IMAP4.error as e:
            self.stderr.write(self.style.ERROR(f"❌ Ошибка IMAP: {e}"))
            self.log_smtp_check(user_smtp, False, f"Ошибка IMAP при чтении: {e}")
            return {'found': 0, 'saved': 0, 'smtp_success': False}
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Ошибка: {e}"))
            self.log_smtp_check(user_smtp, False, f"Ошибка: {e}", traceback.format_exc())
            return {'found': 0, 'saved': 0, 'smtp_success': False}

    def save_message_to_db(self, user, from_email, subject, body, imap_id, received_date=None):
        """Сохраняет письмо в базу данных"""
        try:
            # Проверяем, не сохранено ли уже
            if Message.objects.filter(custom_id__icontains=imap_id[:8]).exists():
                self.stdout.write("   ⏭️ Письмо уже существует, пропускаем")
                return False

            # Создаем сообщение с правильной датой
            message = Message(
                user=user,
                clients=user.email,
                subject=subject,
                message=body,
                message_type='incoming',
            )

            # Если есть дата письма, используем её
            if received_date:
                message.created_at = received_date

            message.save()

            # Отмечаем как прочитанное владельцем
            message.read_by.add(user)

            self.stdout.write(self.style.SUCCESS(f"   ✅ Сохранено: {message.custom_id}"))
            return True

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"   ❌ Ошибка сохранения: {e}"))
            return False