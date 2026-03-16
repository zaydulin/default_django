# management/commands/check_mass_mail_campaigns.py

from django.core.management.base import BaseCommand
from django.core.mail import get_connection, EmailMessage
from django.utils import timezone
from django.conf import settings
from django.db.models import Q
from mail.models import MassMailCampaign, MassMailLog, UserSettingsSMTP
import logging
import sys

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Проверяет запланированные массовые рассылки и запускает отправку для тех, у которых наступило время'

    def add_arguments(self, parser):
        parser.add_argument(
            '--campaign-id',
            type=int,
            help='ID конкретной кампании для проверки (опционально)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Принудительно запустить отправку, даже если время еще не наступило',
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
            # Принудительно запускаем конкретную кампанию
            campaigns = MassMailCampaign.objects.filter(id=campaign_id)
            status_text = f"принудительный запуск кампании ID {campaign_id}"
        elif campaign_id:
            # Проверяем конкретную кампанию по времени
            campaigns = MassMailCampaign.objects.filter(
                Q(id=campaign_id) &
                Q(status='scheduled') &
                Q(scheduled_time__lte=timezone.now())
            )
            status_text = f"проверка кампании ID {campaign_id}"
        else:
            # Проверяем все запланированные кампании
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

        # Проверяем наличие кампаний
        if not campaigns.exists():
            self.stdout.write(self.style.WARNING('❌ Нет кампаний для отправки'))
            return

        self.stdout.write(self.style.SUCCESS(f'✅ Найдено кампаний для отправки: {campaigns.count()}\n'))

        # Обрабатываем каждую кампанию
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
        self.stdout.write(f'   ⚡ Приоритет: {campaign.get_priority_display()}')
        self.stdout.write(f'   📝 Тема: {campaign.subject}')

        # Получаем список получателей
        recipients = campaign.get_recipients_list()
        self.stdout.write(f'   👥 Получателей: {len(recipients)}')

        if not recipients:
            self.stdout.write(self.style.ERROR('   ❌ НЕТ ПОЛУЧАТЕЛЕЙ!'))
            # Логируем ошибку в кампанию
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
            # Логируем ошибку в кампанию
            MassMailLog.objects.create(
                campaign=campaign,
                email='system',
                status='failed',
                error_message='Не найдены SMTP настройки'
            )
            return

        self.stdout.write(f'   📨 SMTP: {smtp_settings.email_host}:{smtp_settings.email_port}')
        self.stdout.write(
            f'   ✉️ Отправитель: {campaign.from_email or smtp_settings.default_from_email or settings.DEFAULT_FROM_EMAIL}')

        # Проверяем, не была ли уже отправлена
        if campaign.status == 'sent' and not force:
            self.stdout.write(
                self.style.WARNING('   ⚠️ Кампания уже отправлена. Используйте --force для повторной отправки'))
            return

        if dry_run:
            self.stdout.write(self.style.WARNING('   🔸 DRY RUN: отправка не производится'))
            return

        # Запускаем отправку
        self.stdout.write(self.style.SUCCESS('   🚀 ЗАПУСК ОТПРАВКИ...'))
        success, result = self.send_campaign(campaign, smtp_settings, recipients, no_progress)

        if success:
            self.stdout.write(self.style.SUCCESS(f'\n   ✅ ОТПРАВКА ЗАВЕРШЕНА:'))
            self.stdout.write(f'      ✓ Успешно: {result["sent"]}')
            self.stdout.write(f'      ✗ Ошибок: {result["failed"]}')
            self.stdout.write(f'      📊 Всего: {result["total"]}')
        else:
            self.stdout.write(self.style.ERROR(f'\n   ❌ ОШИБКА ОТПРАВКИ: {result}'))

    def get_smtp_settings(self, campaign):
        """Получение SMTP настроек для кампании"""
        if campaign.use_smtp_settings:
            return campaign.use_smtp_settings

        # Пробуем получить настройки пользователя
        try:
            return UserSettingsSMTP.objects.get(user=campaign.user)
        except UserSettingsSMTP.DoesNotExist:
            return None

    def send_campaign(self, campaign, smtp_settings, recipients, no_progress=False):
        """Отправка писем для кампании"""

        # Обновляем статус кампании
        campaign.status = 'sending'
        campaign.total_recipients = len(recipients)
        campaign.sent_count = 0
        campaign.failed_count = 0
        campaign.save(update_fields=['status', 'total_recipients', 'sent_count', 'failed_count', 'updated_at'])

        connection = None
        stats = {'sent': 0, 'failed': 0, 'total': len(recipients)}

        try:
            # Создаем подключение к SMTP
            connection = get_connection(
                host=smtp_settings.email_host,
                port=int(smtp_settings.email_port) if smtp_settings.email_port else 587,
                username=smtp_settings.email_host_user,
                password=smtp_settings.email_host_password,
                use_tls=smtp_settings.email_use_tls,
                use_ssl=smtp_settings.email_use_ssl,
                fail_silently=False,
                timeout=30,
            )

            # Подготавливаем базовое письмо
            from_email = campaign.from_email or smtp_settings.default_from_email or settings.DEFAULT_FROM_EMAIL

            # Добавляем шапку и подвал, если есть
            message_body = campaign.message
            if smtp_settings.message_header:
                message_body = smtp_settings.message_header + '\n\n' + message_body
            if smtp_settings.message_footer:
                message_body = message_body + '\n\n' + smtp_settings.message_footer

            self.stdout.write(f'   📨 Начало отправки {len(recipients)} писем...')

            # Отправляем каждому получателю
            for i, email in enumerate(recipients, 1):
                try:
                    # Создаем письмо
                    msg = EmailMessage(
                        subject=campaign.subject,
                        body=message_body,
                        from_email=from_email,
                        to=[email],
                        connection=connection,
                    )

                    # Отправляем
                    msg.send()

                    # Логируем успех
                    MassMailLog.objects.create(
                        campaign=campaign,
                        email=email,
                        status='sent',
                        created_at=timezone.now()
                    )

                    stats['sent'] += 1
                    campaign.sent_count = stats['sent']

                    # Показываем прогресс
                    if not no_progress:
                        progress_msg = f'      Прогресс: {i}/{len(recipients)} писем (✓:{stats["sent"]} ✗:{stats["failed"]})'
                        self.stdout.write(progress_msg, ending='\r')
                        self.stdout.flush()

                    # Сохраняем прогресс каждые 10 писем
                    if i % 10 == 0:
                        campaign.save(update_fields=['sent_count', 'failed_count'])

                except Exception as e:
                    # Логируем ошибку
                    MassMailLog.objects.create(
                        campaign=campaign,
                        email=email,
                        status='failed',
                        error_message=str(e)[:255],  # Обрезаем длинное сообщение
                        created_at=timezone.now()
                    )

                    stats['failed'] += 1
                    campaign.failed_count = stats['failed']

                    logger.error(f'Failed to send to {email}: {str(e)}')

            # Очищаем строку прогресса
            if not no_progress:
                self.stdout.write(' ' * 80, ending='\r')

            # Завершаем кампанию
            campaign.status = 'sent'
            campaign.sent_at = timezone.now()
            campaign.save(update_fields=['status', 'sent_count', 'failed_count', 'sent_at', 'updated_at'])

            return True, stats

        except Exception as e:
            # Критическая ошибка
            campaign.status = 'cancelled'
            campaign.save(update_fields=['status', 'updated_at'])

            # Логируем критическую ошибку
            MassMailLog.objects.create(
                campaign=campaign,
                email='system',
                status='failed',
                error_message=f'Критическая ошибка: {str(e)}',
                created_at=timezone.now()
            )

            logger.exception(f'Fatal error in campaign {campaign.id}: {str(e)}')
            return False, str(e)

        finally:
            if connection:
                connection.close()