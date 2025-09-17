from django.db import models
from django.conf import settings
import os
import uuid
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.
class Stopwords(models.Model):
    """Стоп слова"""
    id = models.AutoField(primary_key=True)
    name = models.CharField("Стоп слова", max_length=120)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Стоп слово"
        verbose_name_plural = "Стоп слова"


class Subscriptions(models.Model):
    """Подписки"""
    email = models.CharField(blank=True, verbose_name='Email', unique=True, max_length=500, null=True)
    create = models.DateTimeField(auto_now=True, blank=True,null=True)

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Подписки"
        verbose_name_plural = "Подписки"


class Collaborations(models.Model):
    name = models.TextField(verbose_name='Имя')
    email = models.TextField(verbose_name='Электронная почта')
    subject = models.TextField(verbose_name='Обьект сотрудничества')
    phone = models.TextField(verbose_name='Номер телефона')
    message = models.TextField(verbose_name='Сообщение')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Запрос на сотрудничество"
        verbose_name_plural = "Запросы на сотрудничество"



class Notificationgroups(models.Model):
    """Уведомление"""
    user = models.ManyToManyField(settings.AUTH_USER_MODEL,verbose_name='Пользователь')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, limit_choices_to={'model__in': ('blogs', 'pages','categorysblogs', 'tagsblogs',)})
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    created_at = models.DateTimeField('Время отправки', auto_now_add=True)
    message = models.TextField()
    slug = models.TextField(editable=False)

    class Meta:
        verbose_name = "Груповое уведомление"
        verbose_name_plural = "Груповые уведомления"