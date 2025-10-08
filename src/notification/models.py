from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.

class Notification(models.Model):
    """Персона"""
    TYPE = [
        (1, 'Регистрация'),
        (2, 'Покупка'),
        (3, 'Сбросить пароль'),
        (4, 'Поддержка'),
    ]
    type = models.PositiveSmallIntegerField('Тип', unique=True, choices=TYPE, blank=False, default=1)
    STATUS = [
        (1, 'Не прочитан'),
        (2, 'Прочитан'),
    ]
    status = models.PositiveSmallIntegerField("Статус", choices=STATUS, blank=False, default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='Пользователь',on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'model__in': ('blogs', 'pages','categorysblogs', 'tagsblogs',)})
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField('Время отправки',auto_now_add=True)
    message = models.TextField()

    class Meta:
        verbose_name = "Уведомление"
        verbose_name_plural = "Уведомление"
