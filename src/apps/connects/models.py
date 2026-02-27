from django.db import models
from django.contrib.auth.models import User
import json
from django.conf import settings



class Chats(models.Model):
    """Модель чатов"""
    userabstract = models.ManyToManyField('Userabstractes', verbose_name="Участники чата")
    create = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Чат"
        verbose_name_plural = "Чаты"
        db_table = 'chats'

    def __str__(self):
        return f"Чат #{self.id} от {self.create}"


class Userabstractes(models.Model):
    """Модель абстрактного пользователя"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Пользователь", null=True, blank=True)
    phone = models.CharField("Телефон", max_length=20, blank=True)
    telegram = models.CharField("Telegram", max_length=100, blank=True)
    whatsapp = models.CharField("WhatsApp", max_length=100, blank=True)
    viber = models.CharField("Viber", max_length=100, blank=True)
    create = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Абстрактный пользователь"
        verbose_name_plural = "Абстрактные пользователи"
        db_table = 'userabstractes'

    def __str__(self):
        contacts = []
        if self.phone: contacts.append(f"тел:{self.phone}")
        if self.telegram: contacts.append(f"tg:{self.telegram}")
        if self.whatsapp: contacts.append(f"wa:{self.whatsapp}")
        if self.viber: contacts.append(f"vb:{self.viber}")
        return f"Пользователь #{self.id}: {', '.join(contacts) if contacts else 'нет контактов'}"


class Messages(models.Model):
    """Модель сообщений"""
    message = models.TextField("Текст сообщения")
    create = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        db_table = 'messages'

    def __str__(self):
        return f"Сообщение #{self.id} от {self.create}"


class MessagesInfo(models.Model):
    """Модель информации о сообщении"""
    message = models.ForeignKey(Messages, on_delete=models.CASCADE, verbose_name="Сообщение", related_name='info')
    json = models.JSONField("JSON данные", default=dict, blank=True)
    file = models.FileField("Файл", upload_to='message_files/', blank=True, null=True)
    create = models.DateTimeField("Дата создания", auto_now_add=True)

    class Meta:
        verbose_name = "Информация о сообщении"
        verbose_name_plural = "Информация о сообщениях"
        db_table = 'messagesinfo'

    def __str__(self):
        return f"Инфо #{self.id} для сообщения #{self.message_id}"

