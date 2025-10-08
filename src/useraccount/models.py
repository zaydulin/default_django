from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import (FileExtensionValidator)
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
import uuid
from uuid import uuid4



def get_user_dir(instance, filename) -> str:
    extension = filename.split(".")[-1]
    return f"users/user_{instance.id}.{extension}"

class Profile(AbstractUser):
    """Персона"""
    GENDER_CHOICE = [
        (1, 'Мужской'),
        (2, 'Женский'),
    ]
    TYPE = [
        (0, 'Сотрудник'),
        (1, 'Обычный'),
        (2, 'Юр лицо'),
    ]
    type = models.PositiveSmallIntegerField('Пол', choices=TYPE, blank=False, default=1)
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(blank=True, verbose_name='Телефон', max_length=500, null=True)
    avatar = models.FileField(upload_to=get_user_dir, blank=True, verbose_name='Аватар', default='default/user-nophoto.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    gender = models.PositiveSmallIntegerField('Пол', choices=GENDER_CHOICE, blank=False, default=1)
    birthday = models.DateField(verbose_name='Дата рождения', blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, verbose_name='Город',null=True)
    middle_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='Отчество')
    online = models.BooleanField(default=False, verbose_name="Онлайн")
    blocked = models.BooleanField(default=False, verbose_name="Заблокирован")
    deleted = models.BooleanField(default=False, verbose_name="Удален")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Passport(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,verbose_name='Пользователь',on_delete=models.CASCADE)
    passport_issued_by_whom = models.TextField("Кем выдан", blank=True, null=True)
    passport_date_of_issue = models.DateField(verbose_name='Дата выдачи', blank=True, null=True)
    passport_the_sub_division_code = models.CharField(max_length=100, blank=True, verbose_name='Код подрозделения',null=True)
    passport_series_and_number = models.CharField(max_length=100, blank=True, verbose_name='Серия и номер',null=True)
    passport_place_of_birth = models.TextField("Место рождения", blank=True, null=True)
    passport_registration = models.TextField("Прописка", blank=True, null=True)
    passport_image_1 = models.FileField(upload_to=get_user_dir, blank=True, verbose_name='Лицевая часть', default='default/user-nophoto.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)
    passport_image_2 = models.FileField(upload_to=get_user_dir, blank=True, verbose_name='Место прописки', default='default/user-nophoto.png', validators=[FileExtensionValidator(allowed_extensions=['png', 'webp', 'jpeg', 'jpg', 'svg'])],)

    class Meta:
        verbose_name = "Паспорт"
        verbose_name_plural = "Паспорта"




