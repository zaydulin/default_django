from django.db import models
from django.conf import settings

# Create your models here.


class Withdrawal(models.Model):
    """Выплаты"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='Пользователь', on_delete=models.CASCADE)
    amount = models.IntegerField("Сумма", blank=True, null=True)
    TYPE_CHOICES = [
        (0, 'Пополнение'),
        (1, 'Списание'),
    ]
    type = models.SmallIntegerField(verbose_name="Пополнение/Списание", choices=TYPE_CHOICES, default=0)
    create = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Выплата"
        verbose_name_plural = "Выплаты"


class Cards(models.Model):
    STATUS =[
        (1, 'Активная'),
        (2, 'Не активная'),
    ]
    card = models.CharField(verbose_name='Карта', max_length=19)
    date = models.DateTimeField('Дата обновления карты', auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,verbose_name='Пользователь', related_name='cardowner')
    status = models.PositiveSmallIntegerField("Статус", default=2, choices=STATUS, blank=False)

    def str(self):
        return f'{self.card}'

    def save(self, *args, **kwargs):
        self.card = self.card.replace("-", "")
        formatted_card = '-'.join([self.card[i:i + 4] for i in range(0, len(self.card), 4)])
        self.card = formatted_card
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Банковская карта"
        verbose_name_plural = "Банковские карты"

class PersonalCards(models.Model):
    STATUS =[
        (1, 'Активная'),
        (2, 'Не активная'),
    ]
    TYPE =[
        (1, 'Стандарт'),
        (2, 'Професиональная'),
        (3, 'Вип'),
    ]
    card = models.CharField(verbose_name='Карта', max_length=19)
    discount = models.CharField(verbose_name='Скидка', max_length=19)
    date = models.DateTimeField('Дата обновления карты', auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,verbose_name='Пользователь')
    status = models.PositiveSmallIntegerField("Статус", default=2, choices=STATUS, blank=False)
    type = models.PositiveSmallIntegerField("Тип", default=1, choices=TYPE, blank=False)

    def str(self):
        return f'{self.card}'


    class Meta:
        verbose_name = "Личная карта"
        verbose_name_plural = "Личные карты"