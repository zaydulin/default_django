# management/commands/check_mass_mail_campaigns.py

from django.core.management.base import BaseCommand
from django.core.mail import get_connection, EmailMultiAlternatives
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from mail.models import MassMailCampaign, MassMailLog, UserSettingsSMTP
import logging
import time
import smtplib
import ssl
import sys

logger = logging.getLogger(__name__)


class EmailService:
    """Сервис для отправки email с поддержкой SMTP настроек"""

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
                correct_login = from_email or smtp_settings.default_from_email
                if correct_login and '@' in correct_login:
                    print(f"   🔧 Исправляем логин: '{smtp_settings.email_host_user}' -> '{correct_login}'")
                    smtp_settings.email_host_user = correct_login
                else:
                    print(f"   ⚠️ Не могу исправить логин, нет правильного email")

            # Для Beget порт должен быть 2525
            if str(smtp_settings.email_port) != '2525':
                print(f"   🔧 Исправляем порт: {smtp_settings.email_port} -> 2525")
                smtp_settings.email_port = 2525

        return smtp_settings

    @staticmethod
    def test_smtp_connection(smtp_settings, stdout=None):
        """
        Тестирование SMTP подключения перед отправкой
        """

        def write_msg(msg):
            if stdout:
                stdout.write(msg)
            else:
                print(msg)

        try:
            write_msg(f"\n   📧 Тестируем SMTP подключение:")
            write_msg(f"      Host: {smtp_settings.email_host}")
            write_msg(f"      Port: {smtp_settings.email_port}")
            write_msg(f"      User: {smtp_settings.email_host_user}")
            write_msg(f"      TLS: {smtp_settings.email_use_tls}")
            write_msg(f"      SSL: {smtp_settings.email_use_ssl}")

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
                server.ehlo()

                if smtp_settings.email_use_tls:
                    write_msg("      🔐 Запускаем STARTTLS...")
                    server.starttls(context=ssl.create_default_context())
                    server.ehlo()

            write_msg("      🔑 Авторизуемся...")
            if smtp_settings.email_host_user and smtp_settings.email_host_password:
                login_result = server.login(smtp_settings.email_host_user, smtp_settings.email_host_password)
                write_msg(f"      ✅ Авторизация успешна!")

            server.quit()
            write_msg("      ✅ Тест подключения пройден успешно")
            return True, "Подключение успешно"

        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"❌ Ошибка аутентификации: {str(e)}"
            write_msg(f"      {error_msg}")
            return False, error_msg
        except Exception as e:
            error_msg = f"❌ Ошибка подключения: {str(e)}"
            write_msg(f"      {error_msg}")
            return False, error_msg

    @staticmethod
    def prepare_message(campaign, smtp_settings=None):
        """
        Подготовка сообщения с учетом шапки и подвала
        """
        full_message = campaign.message

        # Добавляем шапку если есть
        if smtp_settings and smtp_settings.message_header:
            full_message = smtp_settings.message_header + '\n\n' + full_message

        # Добавляем подвал если есть
        if smtp_settings and smtp_settings.message_footer:
            full_message = full_message + '\n\n' + smtp_settings.message_footer

        # Создаем HTML версию
        try:
            context = {
                'message': campaign.message,
                'subject': campaign.subject,
                'user': campaign.user,
            }

            if smtp_settings:
                context['header'] = smtp_settings.message_header
                context['footer'] = smtp_settings.message_footer

            html_message = render_to_string('moderation/mail/email_template.html', context)
        except Exception as e:
            print(f"   ⚠️ Ошибка создания HTML шаблона: {str(e)}")
            html_message = None

        # Если HTML есть — делаем текстовую версию
        if html_message:
            text_message = strip_tags(html_message)
        else:
            text_message = full_message

        return text_message, html_message

    @staticmethod
    def send_batch(campaign, smtp_settings, batch_recipients, batch_num, total_batches, no_progress=False, stdout=None):
        """
        Отправка одного батча писем
        """

        def write_msg(msg, ending='\n'):
            if stdout:
                stdout.write(msg)
            else:
                print(msg, end=ending)

        batch_stats = {'sent': 0, 'failed': 0}

        # Подготавливаем письмо
        text_message, html_message = EmailService.prepare_message(campaign, smtp_settings)

        # Определяем отправителя - ВАЖНО: используем email из SMTP, а не из кампании!
        # Для beget.com нужно использовать именно email_host_user
        if 'beget.com' in smtp_settings.email_host:
            from_email = smtp_settings.email_host_user
            write_msg(f"   📌 Для Beget используем email из SMTP: {from_email}")
        else:
            from_email = campaign.from_email or smtp_settings.default_from_email or settings.DEFAULT_FROM_EMAIL

        # Создаем подключение
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

        try:
            connection.open()

            for i, email in enumerate(batch_recipients, 1):
                try:
                    msg = EmailMultiAlternatives(
                        subject=campaign.subject,
                        body=text_message,
                        from_email=from_email,
                        to=[email],
                        connection=connection,
                    )

                    if html_message:
                        msg.attach_alternative(html_message, "text/html")

                    msg.send()

                    # Логируем успех
                    MassMailLog.objects.create(
                        campaign=campaign,
                        email=email,
                        status='sent',
                        created_at=timezone.now()
                    )

                    batch_stats['sent'] += 1
                    campaign.sent_count += 1

                    # Обновляем прогресс
                    if not no_progress:
                        total_processed = campaign.sent_count + campaign.failed_count
                        progress_percent = (total_processed / campaign.total_recipients) * 100
                        progress_msg = f'      📊 Прогресс: {total_processed}/{campaign.total_recipients} ({progress_percent:.1f}%) ✓:{campaign.sent_count} ✗:{campaign.failed_count}'
                        if stdout:
                            stdout.write('\r' + progress_msg)
                        else:
                            print(progress_msg, end='\r')
                            sys.stdout.flush()

                    # Сохраняем прогресс каждые 10 писем
                    if (campaign.sent_count + campaign.failed_count) % 10 == 0:
                        campaign.save(update_fields=['sent_count', 'failed_count'])

                except Exception as e:
                    error_msg = str(e)[:255]
                    write_msg(f"\n   ❌ Ошибка отправки на {email}: {error_msg}")

                    MassMailLog.objects.create(
                        campaign=campaign,
                        email=email,
                        status='failed',
                        error_message=error_msg,
                        created_at=timezone.now()
                    )

                    batch_stats['failed'] += 1
                    campaign.failed_count += 1

                    logger.error(f'Failed to send to {email}: {error_msg}')

            connection.close()

        except Exception as e:
            write_msg(f"\n   ❌ Ошибка батча {batch_num}: {str(e)}")
            # Логируем ошибки для всех получателей в батче
            for email in batch_recipients:
                MassMailLog.objects.create(
                    campaign=campaign,
                    email=email,
                    status='failed',
                    error_message=f'Batch error: {str(e)}',
                    created_at=timezone.now()
                )
                batch_stats['failed'] += 1
                campaign.failed_count += 1

        return batch_stats


class Command(BaseCommand):
    help = 'Проверяет запланированные массовые рассылки и запускает отправку'

    def add_arguments(self, parser):
        parser.add_argument(
            '--campaign-id',
            type=int,
            help='ID конкретной кампании для проверки',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Принудительно запустить отправку',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Режим проверки без фактической отправки',
        )
        parser.add_argument(
            '--no-progress',
            action='store_true',
            help='Не показывать прогресс отправки',
        )

    def handle(self, *args, **options):
        campaign_id = options['campaign_id']
        force = options['force']
        dry_run = options['dry_run']
        no_progress = options['no_progress']

        self.stdout.write(self.style.SUCCESS(f'\n🔍 ПРОВЕРКА ЗАПЛАНИРОВАННЫХ РАССЫЛОК'))
        self.stdout.write(f'{"=" * 60}')
        self.stdout.write(f'📅 Текущее время: {timezone.now().strftime("%d.%m.%Y %H:%M:%S")}')
        self.stdout.write(f'{"=" * 60}\n')

        # Формируем запрос для поиска кампаний
        if force and campaign_id:
            campaigns = MassMailCampaign.objects.filter(id=campaign_id)
            status_text = f"принудительный запуск кампании ID {campaign_id}"
        elif campaign_id:
            campaigns = MassMailCampaign.objects.filter(
                Q(id=campaign_id) &
                Q(status='scheduled') &
                Q(scheduled_time__lte=timezone.now())
            )
            status_text = f"проверка кампании ID {campaign_id}"
        else:
            campaigns = MassMailCampaign.objects.filter(
                Q(status='scheduled') &
                Q(scheduled_time__lte=timezone.now())
            )
            status_text = "все запланированные кампании"

        self.stdout.write(f'📊 Статус: {status_text}')

        if force and campaign_id:
            self.stdout.write(self.style.WARNING('⚠️  РЕЖИМ ПРИНУДИТЕЛЬНОГО ЗАПУСКА'))

        if dry_run:
            self.stdout.write(self.style.WARNING('⚠️  РЕЖИМ DRY RUN (без реальной отправки)\n'))

        if not campaigns.exists():
            self.stdout.write(self.style.WARNING('❌ Нет кампаний для отправки'))
            return

        self.stdout.write(self.style.SUCCESS(f'✅ Найдено кампаний для отправки: {campaigns.count()}\n'))

        for campaign in campaigns:
            self.process_campaign(campaign, force, dry_run, no_progress)

    def process_campaign(self, campaign, force=False, dry_run=False, no_progress=False):
        """Обработка отдельной кампании"""
        self.stdout.write(f'\n{"-" * 60}')
        self.stdout.write(f'📧 КАМПАНИЯ: "{campaign.name}" (ID: {campaign.id})')
        self.stdout.write(f'{"-" * 60}')
        self.stdout.write(f'   📊 Статус: {campaign.get_status_display()}')
        self.stdout.write(
            f'   📅 Запланирована: {campaign.scheduled_time.strftime("%d.%m.%Y %H:%M") if campaign.scheduled_time else "не запланирована"}')
        self.stdout.write(f'   📝 Тема: {campaign.subject}')

        # Получаем настройки отправки
        batch_size = campaign.message_count or 50
        message_interval = campaign.message_interval or 2

        self.stdout.write(f'   ⚙️ Настройки отправки:')
        self.stdout.write(f'      📦 Писем за раз: {batch_size}')
        self.stdout.write(f'      ⏱️ Интервал между письмами: {message_interval} сек')

        # Получаем список получателей
        recipients = campaign.get_recipients_list()
        self.stdout.write(f'   👥 Получателей: {len(recipients)}')

        if not recipients:
            self.stdout.write(self.style.ERROR('   ❌ НЕТ ПОЛУЧАТЕЛЕЙ!'))
            MassMailLog.objects.create(
                campaign=campaign,
                email='system',
                status='failed',
                error_message='Нет получателей для рассылки'
            )
            return

        # Проверяем SMTP настройки
        smtp_settings = self.get_smtp_settings(campaign)
        if not smtp_settings:
            self.stdout.write(self.style.ERROR('   ❌ НЕТ SMTP НАСТРОЕК!'))
            MassMailLog.objects.create(
                campaign=campaign,
                email='system',
                status='failed',
                error_message='Не найдены SMTP настройки'
            )
            return

        # Исправляем SMTP настройки для Beget
        from_email = campaign.from_email or smtp_settings.default_from_email
        smtp_settings = EmailService.fix_smtp_settings(smtp_settings, from_email)

        self.stdout.write(f'   📨 SMTP: {smtp_settings.email_host}:{smtp_settings.email_port}')

        # Для Beget обязательно используем email_host_user как отправителя
        if 'beget.com' in smtp_settings.email_host:
            actual_from_email = smtp_settings.email_host_user
            self.stdout.write(f'   ✉️ Отправитель (исправлен для Beget): {actual_from_email}')
        else:
            actual_from_email = from_email or smtp_settings.email_host_user
            self.stdout.write(f'   ✉️ Отправитель: {actual_from_email}')

        # Проверяем, не была ли уже отправлена
        if campaign.status == 'sent' and not force:
            self.stdout.write(
                self.style.WARNING('   ⚠️ Кампания уже отправлена. Используйте --force для повторной отправки'))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING('   🔸 DRY RUN: отправка не производится'))
            return

        # Тестируем SMTP подключение
        self.stdout.write(f'   🔌 Тестируем SMTP подключение...')
        success, error_msg = EmailService.test_smtp_connection(smtp_settings, self.stdout)
        if not success:
            self.stdout.write(self.style.ERROR(f'   ❌ SMTP тест не пройден: {error_msg}'))
            MassMailLog.objects.create(
                campaign=campaign,
                email='system',
                status='failed',
                error_message=f'SMTP connection failed: {error_msg}',
                created_at=timezone.now()
            )
            return

        # Запускаем отправку
        self.stdout.write(self.style.SUCCESS('   🚀 ЗАПУСК ОТПРАВКИ...'))

        # Обновляем статус кампании
        campaign.status = 'sending'
        campaign.total_recipients = len(recipients)
        campaign.sent_count = 0
        campaign.failed_count = 0
        campaign.save(update_fields=['status', 'total_recipients', 'sent_count', 'failed_count', 'updated_at'])

        start_time = time.time()

        # Разбиваем получателей на батчи
        batches = [recipients[i:i + batch_size] for i in range(0, len(recipients), batch_size)]

        self.stdout.write(f'   📦 Разбито на {len(batches)} батчей по {batch_size} писем')
        self.stdout.write(f'   ⏱️ Интервал между письмами: {message_interval} сек\n')

        total_stats = {'sent': 0, 'failed': 0}

        for batch_idx, batch in enumerate(batches, 1):
            batch_start_time = time.time()

            self.stdout.write(f'   🚀 Батч {batch_idx}/{len(batches)} ({len(batch)} писем)...')

            # Отправляем батч
            batch_stats = EmailService.send_batch(
                campaign, smtp_settings, batch,
                batch_idx, len(batches), no_progress, self.stdout
            )

            total_stats['sent'] += batch_stats['sent']
            total_stats['failed'] += batch_stats['failed']

            batch_duration = time.time() - batch_start_time
            self.stdout.write(f'      ✅ Батч {batch_idx} завершен за {batch_duration:.2f} сек')

            # Сохраняем прогресс
            campaign.save(update_fields=['sent_count', 'failed_count'])

            # Ждем между батчами
            if batch_idx < len(batches) and message_interval > 0:
                self.stdout.write(f'      ⏳ Ожидание {message_interval} сек перед следующим батчем...')
                time.sleep(message_interval)

        # Очищаем строку прогресса
        if not no_progress:
            self.stdout.write(' ' * 80)

        # Завершаем кампанию
        campaign.status = 'sent'
        campaign.sent_at = timezone.now()
        campaign.save(update_fields=['status', 'sent_count', 'failed_count', 'sent_at', 'updated_at'])

        total_duration = time.time() - start_time

        self.stdout.write(self.style.SUCCESS(f'\n   ✅ ОТПРАВКА ЗАВЕРШЕНА:'))
        self.stdout.write(f'      ✓ Успешно: {total_stats["sent"]}')
        self.stdout.write(f'      ✗ Ошибок: {total_stats["failed"]}')
        self.stdout.write(f'      📊 Всего: {len(recipients)}')
        self.stdout.write(f'      ⏱️ Время выполнения: {total_duration:.2f} сек')

    def get_smtp_settings(self, campaign):
        """Получение SMTP настроек для кампании"""
        if campaign.use_smtp_settings:
            return campaign.use_smtp_settings

        try:
            return UserSettingsSMTP.objects.get(user=campaign.user)
        except UserSettingsSMTP.DoesNotExist:
            return None