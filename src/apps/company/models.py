from django.db import models
from django.conf import settings

# Create your models here.

class Company(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL,verbose_name='Пользователь',on_delete=models.CASCADE)
    company_name = models.CharField(max_length=100, blank=True, verbose_name='Название организации',null=True)
    company_director = models.CharField(max_length=100, blank=True, verbose_name='Руководитель',null=True)
    company_address = models.CharField(max_length=100, blank=True, verbose_name='Юридический адрес',null=True)
    company_nalogovaya = models.CharField(max_length=100, blank=True, verbose_name='Налоговый орган',null=True)
    company_ogrn = models.CharField(max_length=100, blank=True, verbose_name='ОГРН',null=True)
    company_inn = models.CharField(max_length=100, blank=True, verbose_name='ИНН',null=True)
    company_kpp = models.CharField(max_length=100, blank=True, verbose_name='КПП',null=True)
    company_data_registration = models.DateField(verbose_name='Дата регистрации', blank=True, null=True)
    company_type_activity = models.TextField("Основной вид деятельности", blank=True, null=True)

    class Meta:
        verbose_name = "Компания"
        verbose_name_plural = "Компании"