from django.db import models
from ckeditor.fields import RichTextField
from django.urls import reverse
from django.conf import settings
from django.core.validators import (FileExtensionValidator)
import os


class Pages(models.Model):
    """Страницы"""
    PAGETYPE = [
        (1, 'Стандартная'),
        (2, 'Пользовательское соглашение'),
        (3, 'Политика конфедециальности'),
        (4, 'Политика Cookie - Файлов'),
        (5, 'Согласия на обработку персональных данных'),
    ]
    pagetype = models.PositiveSmallIntegerField('Тип', choices=PAGETYPE, blank=False, default=1)
    name = models.CharField("Название", max_length=250)
    description = RichTextField("Описание", blank=True, null=True)
    slug = models.SlugField(max_length=140, unique=True)
    previev = models.FileField(upload_to='pages/%Y/%m/%d/', blank=True, null=True, verbose_name="Превью", default='default/imagegallery/imagegellery_images.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    title = models.CharField(verbose_name="Мета-заголовок", max_length=150, blank=True, null=True,)
    metadescription = models.CharField(verbose_name="Мета-описание", max_length=255, blank=True, null=True,)
    propertytitle = models.CharField(verbose_name="Мета-заголовок ссылки", max_length=150, blank=True, null=True,)
    propertydescription = models.CharField(verbose_name="Мета-описание ссылки", max_length=255, blank=True, null=True,)
    publishet = models.BooleanField("Опубликован", default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"

