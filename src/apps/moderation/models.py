from django.db import models
from django.conf import settings
import os
import uuid
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from multiselectfield import MultiSelectField


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


class Groups(models.Model):
    TYPE_OPTIONS = (
        ("Статистика", (
            ("statistic_generate", "Генерация"),
            ("statistic_view", "Просмотр"),
        )),
        ("Группы", (
            ("groups_list", "Список"),
            ("groups_create", "Создание"),
            ("groups_edit", "Редактирование"),
            ("groups_delete", "Удаление"),
        )),
        ("Сотрудники", (
            ("employees_list", "Список"),
            ("employees_create", "Создание"),
            ("employees_edit", "Редактирование"),
            ("employees_delete", "Удаление"),
        )),
        ("Клиенты", (
            ("clients_list", "Список"),
            ("clients_create", "Создание"),
            ("clients_edit", "Редактирование"),
            ("clients_delete", "Удаление"),
        )),
        ("База знаний", (
            ("knowledge_list", "Список"),
            ("knowledge_create", "Создание"),
            ("knowledge_edit", "Редактирование"),
            ("knowledge_delete", "Удаление"),
        )),
        ("Пользователи", (
            ("clients_list", "Список"),
            ("clients_create", "Создание"),
            ("clients_edit", "Редактирование"),
            ("clients_delete", "Удаление"),
        )),
        ("Email", (
            ("email_send", "Отправка"),
            ("email_list", "Список"),
        )),
        ("Телефония", (
            ("telephony_list", "Список"),
            ("telephony_call", "Звонок"),
        )),
        ("Проекты", (
            ("projects_list", "Список"),
            ("projects_create", "Создание"),
            ("projects_edit", "Редактирование"),
            ("projects_delete", "Удаление"),
        )),
        ("Проделаные работы", (
            ("works_list", "Список"),
        )),
        ("График", (
            ("schedule_view", "Просмотр"),
            ("schedule_edit", "Редактирование"),
        )),
        ("Задачник", (
            ("tasks_list", "Список"),
            ("tasks_create", "Создание"),
            ("tasks_edit", "Редактирование"),
            ("tasks_delete", "Удаление"),
        )),
        ("Бухгалтерия", (
            ("accounting_view", "Просмотр"),
        )),
        ("Платежи", (
            ("payments_list", "Список"),
            ("payments_create", "Создание"),
        )),
        ("Запросы", (
            ("requests_list", "Список"),
        )),
        ("Хоз.часть", (
            ("admin_part_view", "Просмотр"),
        )),
        ("Урок", (
            ("lesson_list", "Список"),
        )),
        ("Обучение", (
            ("training_list", "Список"),
        )),
        ("Вакансии", (
            ("vacancies_list", "Список"),
            ("vacancies_create", "Создание"),
            ("vacancies_edit", "Редактирование"),
            ("vacancies_delete", "Удаление"),
        )),
        ("Заявки", (
            ("applications_list", "Список"),
            ("applications_create", "Создание"),
        )),
        ("Склады (Магазины)", (
            ("storages_list", "Список"),
            ("storages_create", "Создание"),
            ("storages_edit", "Редактирование"),
            ("storages_delete", "Удаление"),
        )),
        ("Компании", (
            ("companies_list", "Список"),
            ("companies_create", "Создание"),
        )),
        ("Товары", (
            ("products_list", "Список"),
            ("products_create", "Создание"),
            ("products_edit", "Редактирование"),
            ("products_delete", "Удаление"),
        )),
        ("Бренды", (
            ("brends_list", "Список"),
            ("brends_create", "Создание"),
            ("brends_edit", "Редактирование"),
            ("brends_delete", "Удаление"),
        )),
        ("Категории", (
            ("categories_list", "Список"),
            ("categories_create", "Создание"),
        )),
        ("Покупки", (
            ("purchases_list", "Список"),
        )),
        ("Жалобы", (
            ("complaints_list", "Список"),
        )),
        ("Отзывы", (
            ("reviews_list", "Список"),
        )),
        ("Комментарии", (
            ("comments_list", "Список"),
        )),
        ("Вопросы", (
            ("questions_list", "Список"),
        )),
        ("Вариации", (
            ("variations_list", "Список"),
        )),
        ("Валюта", (
            ("currency_list", "Список"),
        )),
        ("Поддержка", (
            ("support_list", "Список"),
        )),
        ("Тикеты", (
            ("tickets_list", "Список"),
        )),
        ("Обращение", (
            ("requests_view", "Просмотр"),
        )),
        ("Домены", (
            ("domains_list", "Список"),
            ("domains_create", "Создание"),
        )),
        ("Програма лояльности", (
            ("loyalty_list", "Список"),
        )),
        ("Уведомления", (
            ("notifications_list", "Список"),
        )),
        ("Языки", (
            ("languages_list", "Список"),
        )),
        ("Интеграции", (
            ("integrations_list", "Список"),
        )),
        ("Блог (Новости)", (
            ("blog_list", "Список"),
        )),
        ("Страницы", (
            ("pages_list", "Список"),
        )),
        ("Благотворительность", (
            ("charity_list", "Список"),
        )),
        ("Галерея", (
            ("gallery_list", "Список"),
        )),
        ("Услуги", (
            ("services_list", "Список"),
        )),
        ("Прайс", (
            ("price_list", "Список"),
        )),
        ("ЧаВо", (
            ("faq_list", "Список"),
        )),
        ("Документация", (
            ("docs_list", "Список"),
        )),
        ("Личные", (
            ("personal_view", "Просмотр"),
        )),
        ("Профиль", (
            ("profile_view", "Просмотр"),
        )),
        ("Начисления", (
            ("charges_list", "Список"),
        )),
    )

    types = MultiSelectField(
        choices=TYPE_OPTIONS,
        blank=True,
        verbose_name="Доступ",
        default=list,
        null=True,
        max_length=5555,
    )
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    slug = models.SlugField(editable=False)
    name = models.CharField(max_length=150, verbose_name="Название")
    users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        verbose_name="Пользователи",
        blank=True,
        related_name="groupsuser",
    )

    def types_count(self):
        """Метод для подсчета количества выбранных опций"""
        return len(self.types)  # Возвращает количество выбранных значений


    def get_types_display(self):
        return ", ".join(dict(self.TYPE_OPTIONS).get(type_id) for type_id in self.types)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"