import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError


class ContactList(models.Model):
    """Список контактов пользователя"""
    name = models.CharField(max_length=255, verbose_name="Название списка")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='contact_lists',
                             verbose_name="Владелец")
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Список контактов"
        verbose_name_plural = "Списки контактов"
        unique_together = ['name', 'user']
        ordering = ['name']

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class Contact(models.Model):
    """Контакт в списке контактов"""
    CONTACT_TYPES = (
        ('email', 'Email'),
        ('phone', 'Телефон'),
        ('telegram', 'Telegram'),
        ('other', 'Другое'),
    )

    contact_list = models.ForeignKey(ContactList, on_delete=models.CASCADE, related_name='contacts',
                                     verbose_name="Список контактов")
    name = models.CharField(max_length=255, verbose_name="Имя контакта")
    contact_type = models.CharField(max_length=50, choices=CONTACT_TYPES, default='email', verbose_name="Тип контакта")
    value = models.CharField(max_length=255, verbose_name="Значение (email/телефон/etc)")
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    is_favorite = models.BooleanField(default=False, verbose_name="Избранный")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Контакт"
        verbose_name_plural = "Контакты"
        ordering = ['name']
        unique_together = ['contact_list', 'value']  # Уникальность значения в пределах списка

    def __str__(self):
        return f"{self.name} ({self.value})"

    def clean(self):
        """Валидация email адреса"""
        if self.contact_type == 'email':
            try:
                validate_email(self.value)
            except ValidationError:
                raise ValidationError({'value': 'Введите корректный email адрес'})


class MessageDir(models.Model):
    """Директория сообщений"""
    name = models.CharField(max_length=255, verbose_name="Название")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='message_dirs',
                             verbose_name="Пользователь")

    class Meta:
        verbose_name = "Директория сообщений"
        verbose_name_plural = "Директории сообщений"
        unique_together = ['name', 'user']

    def __str__(self):
        return f"{self.name} ({self.user.username})"


class MessageRm(models.Model):
    """Удаленные сообщения/метаданные удаления"""
    name = models.CharField(max_length=255, verbose_name="Название")
    key = models.CharField(max_length=255, verbose_name="Ключ")

    class Meta:
        verbose_name = "Удаленное сообщение"
        verbose_name_plural = "Удаленные сообщения"

    def __str__(self):
        return self.name


class MessageMask(models.Model):
    """Маски сообщений для пользователей"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='message_masks',
                             verbose_name="Пользователь")
    mask = models.TextField(verbose_name="Маска")

    class Meta:
        verbose_name = "Маска сообщения"
        verbose_name_plural = "Маски сообщений"

    def __str__(self):
        return f"Маска для {self.user.username}"


class Message(models.Model):
    """Основная модель сообщения"""
    MESSAGE_TYPES = (
        ('incoming', 'Входящее'),
        ('outgoing', 'Исходящее'),
        ('draft', 'Черновик'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages_sent',
                             verbose_name="Отправитель")
    clients = models.TextField(verbose_name="Получатели (email адреса)", blank=True,
                               help_text="Введите email адреса через запятую. Например: user1@example.com, user2@example.com")
    message = models.TextField(verbose_name="Сообщение")
    subject = models.CharField(max_length=255, verbose_name="Тема", blank=True, null=True, default='')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='outgoing',
                                    verbose_name="Тип сообщения")
    message_rm = models.ForeignKey(MessageRm, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='messages', verbose_name="Связанное удаленное сообщение")
    self_field = models.BooleanField(default=False, verbose_name="Для себя")
    dirs = models.ManyToManyField(MessageDir, related_name='messages', verbose_name="Директории", blank=True)
    masks = models.ManyToManyField(MessageMask, related_name='messages', verbose_name="Маски", blank=True)
    read_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='read_messages', blank=True,
                                     verbose_name="Прочитано пользователями")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['-created_at']

    def __str__(self):
        return f"Сообщение {self.id} от {self.user.username}"

    def save(self, *args, **kwargs):
        """Автоматически определяем тип сообщения при сохранении"""
        if not self.message_type and not self.self_field:
            # Проверяем, есть ли email текущего пользователя в получателях
            if self.user and hasattr(self.user, 'email'):
                user_email = self.user.email.lower()
                clients_list = [email.lower() for email in self.get_clients_list()]

                if user_email in clients_list:
                    self.message_type = 'incoming'
                else:
                    self.message_type = 'outgoing'

        super().save(*args, **kwargs)

    def get_clients_list(self):
        """Получить список email адресов получателей"""
        if self.clients:
            emails = [email.strip() for email in self.clients.split(',') if email.strip()]
            seen = set()
            unique_emails = []
            for email in emails:
                if email.lower() not in seen:
                    seen.add(email.lower())
                    unique_emails.append(email)
            return unique_emails
        return []

    def add_clients(self, emails):
        """Добавить получателей (принимает список email или строку с запятыми)"""
        if isinstance(emails, list):
            emails_str = ', '.join(emails)
        else:
            emails_str = emails

        if self.clients:
            current_emails = self.get_clients_list()
            new_emails = [email.strip() for email in emails_str.split(',') if email.strip()]
            all_emails = current_emails + [e for e in new_emails if e not in current_emails]
            self.clients = ', '.join(all_emails)
        else:
            self.clients = emails_str
        self.save()

    def remove_clients(self, emails):
        """Удалить получателей"""
        if isinstance(emails, list):
            emails_to_remove = emails
        else:
            emails_to_remove = [email.strip() for email in emails.split(',') if email.strip()]

        current_emails = self.get_clients_list()
        remaining_emails = [e for e in current_emails if e not in emails_to_remove]

        if remaining_emails:
            self.clients = ', '.join(remaining_emails)
        else:
            self.clients = ''
        self.save()

    def get_related_emails(self):
        """Получить все email адреса, связанные с этим сообщением"""
        emails = set()

        # Email отправителя
        if self.user and self.user.email:
            emails.add(self.user.email.lower())

        # Email из поля clients
        if self.clients:
            for email in self.get_clients_list():
                emails.add(email.lower())

        return list(emails)

class MessageFile(models.Model):
    """Файлы, прикрепленные к сообщениям"""
    file = models.FileField(upload_to='message_files/%Y/%m/%d/', verbose_name="Файл")
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='files', verbose_name="Сообщение")
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата загрузки")

    class Meta:
        verbose_name = "Файл сообщения"
        verbose_name_plural = "Файлы сообщений"

    def __str__(self):
        return f"Файл для {self.message.id}"

class UserSettingsSMTP(models.Model):
    message_header = models.TextField("Шапка сообщения письма", blank=True, null=True)
    message_footer = models.TextField("Подвал сообщения письма", blank=True, null=True)
    email_host = models.TextField("Email Site HOST", blank=True, null=True)
    default_from_email = models.TextField("Email Site HOST", blank=True, null=True)
    email_port = models.TextField("Email Site PORT", blank=True, null=True)
    email_host_user = models.TextField("Email Site User", blank=True, null=True)
    email_host_password = models.TextField("Email Site Password", blank=True, null=True)
    email_use_tls = models.BooleanField("Use TLS", default=False, blank=True, null=True)
    email_use_ssl = models.BooleanField("Use SSL", default=False, blank=True, null=True)
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)



    class Meta:
        verbose_name = "Настройка почты"
        verbose_name_plural = "Настройки почты"


class MassMailCampaign(models.Model):
    """Кампания массовой рассылки"""
    STATUS_CHOICES = (
        ('draft', 'Черновик'),
        ('scheduled', 'Запланирована'),
        ('sending', 'Отправляется'),
        ('sent', 'Отправлена'),
        ('cancelled', 'Отменена'),
    )

    PRIORITY_CHOICES = (
        ('low', 'Низкий'),
        ('normal', 'Средний'),
        ('high', 'Высокий'),
    )

    name = models.CharField(max_length=255, verbose_name="Название рассылки")
    subject = models.CharField(max_length=255, verbose_name="Тема письма")
    message = models.TextField(verbose_name="Текст письма")

    # Получатели
    recipient_emails = models.TextField(verbose_name="Email получателей", blank=True,
                                        help_text="Email адреса через запятую или по одному в строке")
    recipient_file = models.FileField(upload_to='mailing_lists/%Y/%m/', verbose_name="Файл со списком рассылки",
                                      blank=True, null=True)

    # Настройки
    use_smtp_settings = models.ForeignKey(UserSettingsSMTP, on_delete=models.SET_NULL,
                                          null=True, blank=True, verbose_name="SMTP настройки")
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='normal',
                                verbose_name="Приоритет")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft',
                              verbose_name="Статус")

    # Отправитель
    from_email = models.EmailField(verbose_name="Email отправителя", blank=True, null=True)
    from_name = models.CharField(max_length=255, verbose_name="Имя отправителя", blank=True, null=True)

    # Планирование
    scheduled_time = models.DateTimeField(verbose_name="Время отправки", blank=True, null=True)

    # Статистика
    total_recipients = models.IntegerField(default=0, verbose_name="Всего получателей")
    sent_count = models.IntegerField(default=0, verbose_name="Отправлено")
    failed_count = models.IntegerField(default=0, verbose_name="Ошибок")
    opened_count = models.IntegerField(default=0, verbose_name="Открыто")
    clicked_count = models.IntegerField(default=0, verbose_name="Переходов")

    # Метаданные
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                             related_name='mass_mail_campaigns', verbose_name="Создатель")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    sent_at = models.DateTimeField(verbose_name="Дата отправки", blank=True, null=True)

    class Meta:
        verbose_name = "Кампания массовой рассылки"
        verbose_name_plural = "Кампании массовой рассылки"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.get_status_display()})"

    def get_recipients_list(self):
        """Получить список email получателей"""
        emails = []

        # Из текстового поля
        if self.recipient_emails:
            for line in self.recipient_emails.split('\n'):
                for email in line.split(','):
                    email = email.strip()
                    if email and '@' in email:
                        emails.append(email)

        return list(set(emails))  # Убираем дубликаты


class MassMailLog(models.Model):
    """Лог отправки массовой рассылки"""
    campaign = models.ForeignKey(MassMailCampaign, on_delete=models.CASCADE,
                                 related_name='logs', verbose_name="Кампания")
    email = models.EmailField(verbose_name="Email получателя")
    status = models.CharField(max_length=50, verbose_name="Статус")
    error_message = models.TextField(verbose_name="Ошибка", blank=True, null=True)
    opened_at = models.DateTimeField(verbose_name="Время открытия", blank=True, null=True)
    clicked_at = models.DateTimeField(verbose_name="Время перехода", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    class Meta:
        verbose_name = "Лог массовой рассылки"
        verbose_name_plural = "Логи массовой рассылки"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.campaign.name} - {self.email} - {self.status}"