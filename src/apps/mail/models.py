import uuid
from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.db.models import Max


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


class MessageDirectory(models.Model):
    """Директория сообщений"""
    name = models.CharField(max_length=255, verbose_name="Название")  # Добавил поле name
    number = models.CharField(max_length=10, verbose_name="Номер", unique=True)  # Уникальный номер типа "01", "02"
    user = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='message_directory',
                                  verbose_name="Пользователь")

    class Meta:
        verbose_name = "Директория сообщений"
        verbose_name_plural = "Директории сообщений"
        ordering = ['number']

    def __str__(self):
        users = ", ".join([u.username for u in self.user.all()[:3]])
        if self.user.count() > 3:
            users += f" и еще {self.user.count() - 3}"
        return f"{self.name} ({self.number}) - {users}"


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


class MessageTemplates(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название", blank=True, null=True, default='')
    mask = models.TextField(verbose_name="Маска")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания", blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления", blank=True, null=True)

    class Meta:
        verbose_name = "Шаблон сообщений"
        verbose_name_plural = "Шаблоны сообщений"



class Message(models.Model):
    """Основная модель сообщения"""
    MESSAGE_TYPES = (
        ('incoming', 'Входящее'),
        ('outgoing', 'Исходящее'),
        ('draft', 'Черновик'),
    )

    # Кастомный ID в формате "01-0001"
    custom_id = models.CharField(max_length=20, unique=True, editable=False, verbose_name="Номер сообщения")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, verbose_name="ID")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='messages_sent',
                             verbose_name="Отправитель")
    clients = models.TextField(verbose_name="Получатели (email адреса)", blank=True,
                               help_text="Введите email адреса через запятую. Например: user1@example.com, user2@example.com")
    message = models.TextField(verbose_name="Сообщение")
    subject = models.CharField(max_length=255, verbose_name="Тема", blank=True, null=True, default='')
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='outgoing',
                                    verbose_name="Тип сообщения")
    message_rm = models.ForeignKey('MessageRm', on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='messages', verbose_name="Связанное удаленное сообщение")
    self_field = models.BooleanField(default=False, verbose_name="Для себя")
    dirs = models.ManyToManyField('MessageDir', related_name='messages', verbose_name="Директории", blank=True)
    masks = models.ManyToManyField('MessageMask', related_name='messages', verbose_name="Маски", blank=True)
    read_by = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='read_messages', blank=True,
                                     verbose_name="Прочитано пользователями")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.custom_id} - {self.subject or 'Без темы'}"

    def generate_custom_id(self):
        """
        Генерирует ID в формате "01-0001" на основе директории пользователя
        """
        from django.apps import apps
        import time

        print(f"\n   🔧 GENERATE_CUSTOM_ID called")

        MessageDirectory = apps.get_model('mail', 'MessageDirectory')

        # Значение по умолчанию
        dir_number = "00"
        user_dir = None

        # Пробуем найти директорию, связанную с пользователем
        if hasattr(self, 'user') and self.user and self.user.pk:
            try:
                print(f"   👤 Looking for directory for user: {self.user.username}")

                # Ищем директории, где есть этот пользователь
                user_dirs = MessageDirectory.objects.filter(user=self.user)

                if user_dirs.exists():
                    # Берем первую директорию
                    user_dir = user_dirs.first()
                    if user_dir and user_dir.number:
                        dir_number = str(user_dir.number).zfill(2)
                        print(f"   📁 Found directory: {user_dir.name} with number: {dir_number}")
                else:
                    print(f"   📁 No directory found, creating default...")
                    # Создаем директорию по умолчанию
                    user_dir = self.create_default_directory()
                    if user_dir and user_dir.number:
                        dir_number = str(user_dir.number).zfill(2)
                        print(f"   ✅ Created directory with number: {dir_number}")
            except Exception as e:
                print(f"   ⚠️ Error getting directory: {e}")
                # Продолжаем с dir_number = "00"

        print(f"   📁 Using directory number: {dir_number}")

        # Находим следующий порядковый номер
        max_num = 0
        try:
            # Ищем все сообщения с таким префиксом
            prefix = f"{dir_number}-"
            print(f"   🔍 Looking for messages with prefix: {prefix}")

            # Получаем все сообщения с таким префиксом
            messages = Message.objects.filter(custom_id__startswith=prefix)

            if messages.exists():
                print(f"   📊 Found {messages.count()} messages with this prefix")
                # Извлекаем числовые части
                numbers = []
                for msg in messages:
                    if msg.custom_id and '-' in msg.custom_id:
                        try:
                            num_part = msg.custom_id.split('-')[1]
                            print(f"      - Extracting number from: {msg.custom_id} -> {num_part}")
                            if num_part.isdigit():
                                numbers.append(int(num_part))
                        except (IndexError, ValueError) as e:
                            print(f"      ⚠️ Error extracting number: {e}")
                            continue

                if numbers:
                    max_num = max(numbers)
                    print(f"   📊 Max number found: {max_num}")
            else:
                print(f"   📊 No messages found with prefix {prefix}")
        except Exception as e:
            print(f"   ⚠️ Error finding max number: {e}")

        next_num = max_num + 1
        print(f"   🔢 Next number: {next_num}")

        # Формируем новый ID
        new_id = f"{dir_number}-{next_num:04d}"
        print(f"   🆕 Generated new_id: {new_id}")

        # Проверяем, не существует ли уже такой ID
        attempt = 0
        while Message.objects.filter(custom_id=new_id).exists() and attempt < 10:
            print(f"   ⚠️ ID {new_id} already exists, trying next...")
            next_num += 1
            new_id = f"{dir_number}-{next_num:04d}"
            attempt += 1

        print(f"   ✅ Final custom_id: {new_id}\n")
        return new_id

    def create_default_directory(self):
        """
        Создает директорию по умолчанию для пользователя
        """
        from django.apps import apps
        from django.db import transaction
        from django.db.models import Max

        MessageDirectory = apps.get_model('mail', 'MessageDirectory')

        with transaction.atomic():
            # Находим максимальный номер
            max_obj = MessageDirectory.objects.aggregate(
                Max('number')
            )
            max_number = max_obj['number__max']

            if max_number:
                try:
                    # Пробуем преобразовать в число
                    if max_number.isdigit():
                        next_num = int(max_number) + 1
                    else:
                        # Если не число, ищем первый свободный
                        existing = set(MessageDirectory.objects.values_list('number', flat=True))
                        next_num = 1
                        while f"{next_num:02d}" in existing:
                            next_num += 1
                except (ValueError, AttributeError):
                    next_num = 1
            else:
                next_num = 1

            # Форматируем номер с ведущим нулем
            dir_number = f"{next_num:02d}"

            # Создаем новую директорию
            dir_name = f"Директория пользователя {self.user.username}"

            # Убеждаемся, что такой номер не занят
            while MessageDirectory.objects.filter(number=dir_number).exists():
                next_num += 1
                dir_number = f"{next_num:02d}"

            dir = MessageDirectory.objects.create(
                name=dir_name,
                number=dir_number
            )
            dir.user.add(self.user)

            return dir

    @classmethod
    def get_by_custom_id(cls, custom_id):
        """
        Получить сообщение по кастомному ID
        """
        try:
            return cls.objects.get(custom_id=custom_id)
        except cls.DoesNotExist:
            return None

    @property
    def formatted_id(self):
        """
        Возвращает отформатированный ID для отображения
        """
        return self.custom_id or "---"

    def save(self, *args, **kwargs):
        """Автоматически определяем тип сообщения при сохранении"""
        print(f"\n🔧 SAVE CALLED for message {getattr(self, 'pk', 'NEW')}")
        print(f"   self_field: {self.self_field}")
        print(f"   custom_id before: {self.custom_id}")
        print(f"   pk: {self.pk}")

        # Проверяем, есть ли уже ID в базе
        is_new = True
        if self.pk:
            try:
                # Пробуем найти объект в базе
                existing = Message.objects.get(pk=self.pk)
                is_new = False
                print(f"   Found existing message with pk: {self.pk}")
            except Message.DoesNotExist:
                print(f"   No existing message with pk: {self.pk}")
                is_new = True

        print(f"   is_new (after check): {is_new}")

        # Генерируем custom_id для новых сообщений
        if is_new and not self.custom_id:
            print("   🔄 Generating custom_id...")
            self.custom_id = self.generate_custom_id()
            print(f"   ✅ Generated custom_id: {self.custom_id}")
        elif is_new and self.custom_id:
            print(f"   ℹ️ custom_id already set: {self.custom_id}")
        else:
            print(f"   ℹ️ Existing message, custom_id: {self.custom_id}")

        # Остальная логика...
        if not self.message_type and not self.self_field:
            # Проверяем, есть ли email текущего пользователя в получателях
            if self.user and hasattr(self.user, 'email'):
                user_email = self.user.email.lower()
                clients_list = [email.lower() for email in self.get_clients_list()]
                print(f"   user_email: {user_email}")
                print(f"   clients_list: {clients_list}")

                if user_email in clients_list:
                    self.message_type = 'incoming'
                    print(f"   ✅ message_type set to: incoming")
                else:
                    self.message_type = 'outgoing'
                    print(f"   ✅ message_type set to: outgoing")

        super().save(*args, **kwargs)
        print(f"   ✅ Message saved with custom_id: {self.custom_id}\n")

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
    last_check_time = models.DateTimeField("Время последней проверки", blank=True, null=True)
    last_check_success = models.BooleanField("Последняя проверка успешна", default=False)
    last_error = models.TextField("Последняя ошибка", blank=True, null=True)
    check_count = models.IntegerField("Количество проверок", default=0)
    success_count = models.IntegerField("Количество успешных проверок", default=0)
    failure_count = models.IntegerField("Количество ошибок", default=0)



    class Meta:
        verbose_name = "Настройка почты"
        verbose_name_plural = "Настройки почты"


class SmtpCheckLog(models.Model):
    """Лог проверок SMTP настроек"""
    smtp_settings = models.ForeignKey(UserSettingsSMTP, on_delete=models.CASCADE,
                                      related_name='check_logs', verbose_name="SMTP настройки")
    status = models.CharField(max_length=20, verbose_name="Статус")
    message = models.TextField(verbose_name="Сообщение")
    checked_at = models.DateTimeField(auto_now_add=True, verbose_name="Время проверки")

    class Meta:
        verbose_name = "Лог проверки SMTP"
        verbose_name_plural = "Логи проверки SMTP"
        ordering = ['-checked_at']

    def __str__(self):
        return f"{self.smtp_settings.user.username} - {self.status} - {self.checked_at}"


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