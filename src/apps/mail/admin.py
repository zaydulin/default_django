from django.contrib import admin
from django.utils.html import format_html
from .models import (
    ContactList, Contact, MessageDir, MessageRm, MessageMask,
    Message, MessageFile, UserSettingsSMTP, MassMailCampaign, MassMailLog, MessageDirectory, SmtpCheckLog
)
from django.contrib.auth import get_user_model

from django.db.models import Max
from django.conf import settings
from django.apps import apps
User = get_user_model()


@admin.register(ContactList)
class ContactListAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'contacts_count', 'created_at')
    list_filter = ('user', 'created_at')
    search_fields = ('name', 'user__username', 'user__email')
    readonly_fields = ('created_at', 'updated_at')

    def contacts_count(self, obj):
        count = obj.contacts.count()
        return format_html('<b>{}</b>', count)

    contacts_count.short_description = 'Количество контактов'

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'user', 'description')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'contact_type', 'value', 'contact_list', 'is_favorite', 'created_at')
    list_filter = ('contact_type', 'is_favorite', 'contact_list__user', 'contact_list')
    search_fields = ('name', 'value', 'contact_list__name')
    list_editable = ('is_favorite',)
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        ('Основная информация', {
            'fields': ('contact_list', 'name', 'contact_type', 'value')
        }),
        ('Дополнительно', {
            'fields': ('description', 'is_favorite')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MessageDir)
class MessageDirAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'messages_count')  # Убрали created_at
    list_filter = ('user',)
    search_fields = ('name', 'user__username')

    def messages_count(self, obj):
        count = obj.messages.count()
        return format_html('<b>{}</b>', count)

    messages_count.short_description = 'Количество сообщений'


@admin.register(MessageRm)
class MessageRmAdmin(admin.ModelAdmin):
    list_display = ('name', 'key', 'message_link')
    search_fields = ('name', 'key')

    def message_link(self, obj):
        if hasattr(obj, 'messages') and obj.messages.exists():
            message = obj.messages.first()
            return format_html('<a href="/admin/mail/message/{}/change/">Связанное сообщение</a>', message.id)
        return '-'

    message_link.short_description = 'Связанное сообщение'


@admin.register(MessageMask)
class MessageMaskAdmin(admin.ModelAdmin):
    list_display = ('mask_preview', 'user', 'messages_count')  # Убрали created_at
    list_filter = ('user',)
    search_fields = ('mask', 'user__username')

    def mask_preview(self, obj):
        return obj.mask[:50] + '...' if len(obj.mask) > 50 else obj.mask

    mask_preview.short_description = 'Маска'

    def messages_count(self, obj):
        count = obj.messages.count()
        return format_html('<b>{}</b>', count)

    messages_count.short_description = 'Количество сообщений'


class MessageFileInline(admin.TabularInline):
    model = MessageFile
    extra = 0
    readonly_fields = ('file_link', 'uploaded_at')
    fields = ('file_link', 'uploaded_at')

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Просмотреть файл</a>', obj.file.url)
        return '-'

    file_link.short_description = 'Файл'


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('custom_id', 'user', 'subject_preview', 'message_type', 'message_preview',
                    'recipients_count', 'read_by_count', 'has_files', 'created_at', 'short_uuid')
    list_display_links = ('custom_id', 'subject_preview')  # Чтобы можно было кликнуть по номеру
    list_filter = ('message_type', 'self_field', 'user', 'created_at')
    search_fields = ('custom_id', 'subject', 'message', 'clients', 'user__username', 'user__email')
    readonly_fields = ('id', 'custom_id', 'created_at', 'updated_at', 'full_message',
                       'recipients_list', 'read_by_list', 'short_uuid')
    inlines = [MessageFileInline]
    filter_horizontal = ('dirs', 'masks', 'read_by')

    fieldsets = (
        ('Основная информация', {
            'fields': ('id', 'custom_id', 'user', 'message_type', 'self_field', 'subject')
        }),
        ('Сообщение', {
            'fields': ('full_message',)
        }),
        ('Получатели', {
            'fields': ('clients', 'recipients_list', 'read_by', 'read_by_list')
        }),
        ('Связи', {
            'fields': ('dirs', 'masks', 'message_rm'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def short_uuid(self, obj):
        """Показывает сокращенный UUID для справки"""
        return str(obj.id)[:8] + '...'

    short_uuid.short_description = 'UUID'
    short_uuid.admin_order_field = 'id'  # Можно сортировать по UUID

    def subject_preview(self, obj):
        if obj.subject:
            return obj.subject[:30] + '...' if len(obj.subject) > 30 else obj.subject
        return '(без темы)'

    subject_preview.short_description = 'Тема'
    subject_preview.admin_order_field = 'subject'  # Сортировка по теме

    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message

    message_preview.short_description = 'Сообщение'

    def recipients_count(self, obj):
        count = len(obj.get_clients_list())
        return format_html('<b style="color: {};">{}</b>',
                           '#28a745' if count > 0 else '#6c757d', count)

    recipients_count.short_description = 'Получателей'
    recipients_count.admin_order_field = 'clients'  # Приблизительная сортировка

    def read_by_count(self, obj):
        count = obj.read_by.count()
        total = len(obj.get_clients_list())
        if total > 0:
            percentage = int(count / total * 100)
            return format_html('<b style="color: {};">{} ({}%)</b>',
                               '#28a745' if percentage == 100 else '#ffc107',
                               count, percentage)
        return format_html('<b>{}</b>', count)

    read_by_count.short_description = 'Прочитано'

    def has_files(self, obj):
        if obj.files.exists():
            return format_html('<img src="/static/admin/img/icon-yes.svg" alt="Да" title="Есть файлы">')
        return format_html('<img src="/static/admin/img/icon-no.svg" alt="Нет" title="Нет файлов">')

    has_files.short_description = 'Файлы'

    def full_message(self, obj):
        return format_html(
            '<div style="white-space: pre-wrap; background: #f8f9fa; padding: 15px; border-radius: 5px;">{}</div>',
            obj.message)

    full_message.short_description = 'Полный текст сообщения'

    def recipients_list(self, obj):
        recipients = obj.get_clients_list()
        if recipients:
            items = []
            for email in recipients:
                # Проверяем, есть ли такой пользователь в системе
                try:
                    user = User.objects.get(email=email)
                    items.append(f'<span style="color: #28a745;">✓ {email} ({user.username})</span>')
                except User.DoesNotExist:
                    items.append(f'<span style="color: #ffc107;">○ {email}</span>')
            return format_html('<br>'.join(items))
        return '-'

    recipients_list.short_description = 'Список получателей'

    def read_by_list(self, obj):
        users = obj.read_by.all()
        if users:
            items = []
            for u in users:
                items.append(f'{u.get_full_name() or u.username} <span style="color: #6c757d;">({u.email})</span>')
            return format_html('<br>'.join(items))
        return '-'

    read_by_list.short_description = 'Прочитано пользователями'

    def get_queryset(self, request):
        """Оптимизация запросов"""
        return super().get_queryset(request).select_related(
            'user', 'message_rm'
        ).prefetch_related(
            'dirs', 'masks', 'read_by', 'files'
        )

    def get_readonly_fields(self, request, obj=None):
        """Делаем custom_id только для чтения всегда"""
        readonly = list(self.readonly_fields)
        if 'custom_id' not in readonly:
            readonly.append('custom_id')
        return readonly

    class Media:
        css = {
            'all': ('admin/css/custom_admin.css',)
        }
@admin.register(MessageFile)
class MessageFileAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'file_size', 'message_link', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('file', 'message__subject', 'message__message')
    readonly_fields = ('file_link', 'uploaded_at')

    def file_name(self, obj):
        return obj.file.name.split('/')[-1] if obj.file else '-'

    file_name.short_description = 'Имя файла'

    def file_size(self, obj):
        if obj.file:
            size = obj.file.size
            if size < 1024:
                return f"{size} B"
            elif size < 1024 * 1024:
                return f"{size / 1024:.1f} KB"
            else:
                return f"{size / (1024 * 1024):.1f} MB"
        return '-'

    file_size.short_description = 'Размер'

    def message_link(self, obj):
        return format_html('<a href="/admin/mail/message/{}/change/">Просмотреть сообщение</a>', obj.message.id)

    message_link.short_description = 'Сообщение'

    def file_link(self, obj):
        if obj.file:
            return format_html('<a href="{}" target="_blank">Скачать файл</a>', obj.file.url)
        return '-'

    file_link.short_description = 'Ссылка'


@admin.register(UserSettingsSMTP)
class UserSettingsSMTPAdmin(admin.ModelAdmin):
    list_display = ('user', 'email_host', 'email_port', 'default_from_email',
                    'use_tls_icon', 'use_ssl_icon', 'has_header_footer')
    list_filter = ('email_use_tls', 'email_use_ssl', 'user')
    search_fields = ('user__username', 'user__email', 'email_host', 'default_from_email')
    readonly_fields = ('user',)

    fieldsets = (
        ('Пользователь', {
            'fields': ('user',)
        }),
        ('SMTP настройки', {
            'fields': ('email_host', 'email_port', 'default_from_email',
                       'email_host_user', 'email_host_password')
        }),
        ('Безопасность', {
            'fields': ('email_use_tls', 'email_use_ssl'),
            'description': 'Внимание: TLS и SSL обычно не используются одновременно'
        }),
        ('Шапка и подвал', {
            'fields': ('message_header', 'message_footer'),
            'classes': ('wide',)
        }),
    )

    def use_tls_icon(self, obj):
        if obj.email_use_tls:
            return format_html('<img src="/static/admin/img/icon-yes.svg" alt="Yes">')
        return format_html('<img src="/static/admin/img/icon-no.svg" alt="No">')

    use_tls_icon.short_description = 'TLS'

    def use_ssl_icon(self, obj):
        if obj.email_use_ssl:
            return format_html('<img src="/static/admin/img/icon-yes.svg" alt="Yes">')
        return format_html('<img src="/static/admin/img/icon-no.svg" alt="No">')

    use_ssl_icon.short_description = 'SSL'

    def has_header_footer(self, obj):
        if obj.message_header or obj.message_footer:
            return format_html('<img src="/static/admin/img/icon-yes.svg" alt="Yes">')
        return format_html('<img src="/static/admin/img/icon-no.svg" alt="No">')

    has_header_footer.short_description = 'Шапка/подвал'


class MassMailLogInline(admin.TabularInline):
    model = MassMailLog
    extra = 0
    readonly_fields = ('email', 'status', 'error_message', 'opened_at', 'clicked_at', 'created_at')
    fields = ('email', 'status', 'error_message', 'opened_at', 'clicked_at', 'created_at')
    can_delete = False
    max_num = 20


@admin.register(MassMailCampaign)
class MassMailCampaignAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'subject_preview', 'status_colored',
                    'total_recipients', 'sent_count', 'failed_count', 'progress_bar', 'created_at')
    list_filter = ('status',  'user', 'created_at')
    search_fields = ('name', 'subject', 'message', 'user__username', 'user__email')
    readonly_fields = ('total_recipients', 'sent_count', 'failed_count', 'opened_count',
                       'clicked_count', 'created_at', 'updated_at', 'sent_at', 'recipients_preview')
    inlines = [MassMailLogInline]

    fieldsets = (
        ('Основная информация', {
            'fields': ('name', 'user', 'status')
        }),
        ('Письмо', {
            'fields': ('subject', 'message', 'from_email', 'from_name')
        }),
        ('Получатели', {
            'fields': ('recipient_emails', 'recipient_file', 'recipients_preview', 'total_recipients')
        }),
        ('SMTP настройки', {
            'fields': ('use_smtp_settings',),
            'classes': ('collapse',)
        }),
        ('Планирование', {
            'fields': ('scheduled_time',),
            'classes': ('collapse',)
        }),
        ('Статистика', {
            'fields': ('sent_count', 'failed_count', 'opened_count', 'clicked_count', 'sent_at')
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    def subject_preview(self, obj):
        return obj.subject[:50] + '...' if len(obj.subject) > 50 else obj.subject

    subject_preview.short_description = 'Тема'

    def status_colored(self, obj):
        colors = {
            'draft': '#6c757d',
            'scheduled': '#17a2b8',
            'sending': '#007bff',
            'sent': '#28a745',
            'cancelled': '#dc3545',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#000000'),
            obj.get_status_display()
        )

    status_colored.short_description = 'Статус'




    def progress_bar(self, obj):
        if obj.total_recipients == 0:
            return '-'
        percent = int((obj.sent_count + obj.failed_count) / obj.total_recipients * 100)
        return format_html(
            '<div style="width:100px; background:#e9ecef; border-radius:3px;">'
            '<div style="width:{}%; background:#28a745; height:20px; border-radius:3px; text-align:center; color:white; font-size:11px; line-height:20px;">'
            '{}%</div></div>',
            percent, percent
        )

    progress_bar.short_description = 'Прогресс'

    def recipients_preview(self, obj):
        recipients = obj.get_recipients_list()
        if recipients:
            preview = '<br>'.join(recipients[:10])
            if len(recipients) > 10:
                preview += f'<br>... и ещё {len(recipients) - 10}'
            return format_html(preview)
        return '-'

    recipients_preview.short_description = 'Предпросмотр получателей'


@admin.register(MassMailLog)
class MassMailLogAdmin(admin.ModelAdmin):
    list_display = ('id', 'campaign_link', 'email', 'status_colored', 'created_at', 'opened_at')
    list_filter = ('status', 'created_at', 'campaign__user')
    search_fields = ('email', 'campaign__name', 'error_message')
    readonly_fields = ('campaign', 'email', 'status', 'error_message', 'opened_at', 'clicked_at', 'created_at')

    def campaign_link(self, obj):
        return format_html('<a href="/admin/mail/massmailcampaign/{}/change/">{}</a>',
                           obj.campaign.id, obj.campaign.name)

    campaign_link.short_description = 'Кампания'

    def status_colored(self, obj):
        colors = {
            'pending': '#ffc107',
            'sent': '#28a745',
            'failed': '#dc3545',
            'opened': '#17a2b8',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, '#000000'),
            obj.get_status_display() if hasattr(obj, 'get_status_display') else obj.status
        )

    status_colored.short_description = 'Статус'

admin.site.register(MessageDirectory)
admin.site.register(SmtpCheckLog)
