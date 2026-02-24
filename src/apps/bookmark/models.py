from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

# Create your models here.
class BookmarkGroup(models.Model):
    """Закладка"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL,verbose_name='Пользователь',on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, verbose_name='Название',null=True)
    information = models.TextField( verbose_name='Описание')

    class Meta:
        verbose_name = "Группа закладки"
        verbose_name_plural = "Группы закладок"

class Bookmark(models.Model):
    """Закладка"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь', on_delete=models.CASCADE)
    bookmarkgroup = models.ForeignKey('BookmarkGroup', verbose_name='Вкладка', on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, verbose_name='Название', null=True)
    object_id = models.CharField(max_length=155, verbose_name='ID объекта')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = "Закладка"
        verbose_name_plural = "Закладки"
