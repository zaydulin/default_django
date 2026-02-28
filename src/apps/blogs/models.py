from django.db import models
from ckeditor.fields import RichTextField
from django.urls import reverse
from django.conf import settings
from django.core.validators import (FileExtensionValidator)
import os


class CategorysBlogs(models.Model):
    """Категории"""
    name = models.CharField(max_length=150, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name='URL')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    parent = models.ForeignKey('self', related_name='children', on_delete=models.CASCADE, blank=True, null=True, verbose_name='Родитель')
    cover = models.FileField("Обложка категории",   upload_to="category/%Y/%m/%d/", blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    icon = models.FileField("Иконка категории",   upload_to="category/%Y/%m/%d/", blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    image = models.FileField("Картинка категории",   upload_to="category/%Y/%m/%d/", blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    previev = models.FileField(upload_to='category/%Y/%m/%d/', blank=True, null=True, verbose_name="Превью", default='default/imagegallery/imagegellery_images.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    title = models.CharField(verbose_name="Мета-заголовок", max_length=150, blank=True, null=True,)
    metadescription = models.CharField(verbose_name="Мета-описание", max_length=255, blank=True, null=True,)
    propertytitle = models.CharField(verbose_name="Мета-заголовок ссылки", max_length=150, blank=True, null=True,)
    propertydescription = models.CharField(verbose_name="Мета-описание ссылки", max_length=255, blank=True, null=True,)
    publishet = models.BooleanField("Опубликован", default=False)
    create = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория новости"
        verbose_name_plural = "Категории новости"


class TagsBlogs(models.Model):
    """Метки"""
    name = models.CharField(max_length=150, unique=True, verbose_name='Название')
    slug = models.SlugField(max_length=200, unique=True, blank=True, null=True, verbose_name='URL')
    description = models.TextField(blank=True, null=True, verbose_name='Описание')
    cover = models.FileField("Обложка метки",   upload_to="tags/%Y/%m/%d/", blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    icon = models.FileField("Иконка метки",   upload_to="tags/%Y/%m/%d/", blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    image = models.FileField("Картинка метки",   upload_to="tags/%Y/%m/%d/", blank=True, null=True, validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    previev = models.FileField(upload_to='tags/%Y/%m/%d/', blank=True, null=True, verbose_name="Превью", default='default/imagegallery/imagegellery_images.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    title = models.CharField(verbose_name="Мета-заголовок", max_length=150, blank=True, null=True,)
    metadescription = models.CharField(verbose_name="Мета-описание", max_length=255, blank=True, null=True,)
    propertytitle = models.CharField(verbose_name="Мета-заголовок ссылки", max_length=150, blank=True, null=True,)
    propertydescription = models.CharField(verbose_name="Мета-описание ссылки", max_length=255, blank=True, null=True,)
    publishet = models.BooleanField("Опубликован", default=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Метка новости"
        verbose_name_plural = "Метки новости"


class Blogs(models.Model):
    """Блог"""
    author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Авторы', on_delete=models.CASCADE, blank=True, null=True)
    resource = models.CharField("Источник", max_length=550, blank=True, null=True)
    category = models.ManyToManyField(CategorysBlogs, verbose_name="Категории", blank=True)
    tags = models.ManyToManyField(TagsBlogs, verbose_name="Метки", blank=True)
    name = models.CharField("Название", max_length=250)
    description = RichTextField("Описание", blank=True, null=True)
    previev = models.FileField(upload_to='blogs/%Y/%m/%d/', blank=True, null=True, verbose_name="Превью", default='default/imagegallery/imagegellery_images.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    title = models.CharField(max_length=150, verbose_name='Мета-заголовок', blank=True, null=True)
    metadescription = models.TextField(blank=True, null=True, verbose_name='Мета-описание')
    propertytitle = models.CharField(verbose_name="Мета-заголовок ссылки", max_length=150, blank=True, null=True,)
    propertydescription = models.CharField(verbose_name="Мета-описание ссылки", max_length=255, blank=True, null=True,)
    slug = models.SlugField(max_length=140, unique=True)
    cover = models.FileField("Обложка", upload_to="blogs/%Y/%m/%d/", blank=True, null=True, default='default/blogs/cover.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    image = models.FileField("Изображение", upload_to="blogs/%Y/%m/%d/", blank=True, null=True, default='default/blogs/cover.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    publishet = models.BooleanField("Опубликован", default=False)
    create = models.DateTimeField(auto_now=True, blank=True, null=True)

    def __str__(self):
        return self.name


    class Meta:
        verbose_name = "Статья"
        verbose_name_plural = "Статьи"