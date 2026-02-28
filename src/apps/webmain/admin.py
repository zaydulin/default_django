from django.contrib import admin
from .models import *
from django.utils.html import format_html
from django_ace import AceWidget
from django import forms

class GeneralSettingsForm(forms.ModelForm):
    message_header = forms.CharField(widget=AceWidget(mode='html',readonly=False,behaviours=True,showgutter=True,  wordwrap=False, usesofttabs=True))
    message_footer = forms.CharField(widget=AceWidget(mode='html',readonly=False,behaviours=True,showgutter=True,  wordwrap=False, usesofttabs=True))

@admin.register(Seo)
class SeoAdmin(admin.ModelAdmin):
    model = Seo


@admin.register(SettingsGlobale)
class SettingsGlobaleAdmin(admin.ModelAdmin):
    list_display = ["id",  "name"]
    list_display_links = ["id",  "name"]


@admin.register(Pages)
class PagesAdmin(admin.ModelAdmin):
    """Расширенная админка для модели Pages"""

    # Поля для отображения в списке
    list_display = (
        'name',
        'pagetype',
        'publishet',
        'slug',
        'preview_thumbnail',
        'created_date'
    )

    # Поля по которым можно искать
    search_fields = ('name', 'slug', 'description', 'title', 'metadescription')

    # Поля для фильтрации
    list_filter = ('pagetype', 'publishet')

    # Поля которые можно редактировать прямо в списке
    list_editable = ('publishet',)

    # Поля только для чтения
    readonly_fields = ('preview_thumbnail',)

    # Организация полей по группам
    fieldsets = (
        ('Основная информация', {
            'fields': (
                'pagetype',
                'name',
                'slug',
                'description',
                'templates',
                'publishet'
            ),
        }),
        ('Медиафайлы', {
            'fields': ('previev', 'preview_thumbnail'),
            'classes': ('wide',),
        }),
        ('SEO настройки', {
            'fields': (
                'title',
                'metadescription',
                'propertytitle',
                'propertydescription',
                'keywords'
            ),
            'classes': ('collapse',),  # Скрыто по умолчанию
        }),
    )

    # Предустановленные фильтры
    date_hierarchy = 'create' if hasattr(Pages, 'create') else None

    # Количество записей на странице
    list_per_page = 25

    def preview_thumbnail(self, obj):
        """Миниатюра превью"""
        if obj.previev:
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 50px;" />',
                obj.previev.url
            )
        return "Нет изображения"

    preview_thumbnail.short_description = "Превью"

    def created_date(self, obj):
        """Дата создания (если есть поле create)"""
        if hasattr(obj, 'create'):
            return obj.create.strftime("%d.%m.%Y %H:%M")
        return "-"

    created_date.short_description = "Дата создания"

    # Автоматическое заполнение slug из name
    prepopulated_fields = {'slug': ('name',)}