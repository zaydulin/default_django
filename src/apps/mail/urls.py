from django.urls import path
from . import views

app_name = 'mail'

urlpatterns = [
    # Основные страницы
    path('messages/', views.MessageListView.as_view(), name='message_list'),
    path('messages/<uuid:message_id>/', views.MessageDetailView.as_view(), name='message_detail'),
    path('messages/<uuid:message_id>/view/', views.AllMessageDetailView.as_view(), name='all_message_detail'),
    path('all-messages/', views.AllMessagesListView.as_view(), name='all_messages'),

    # API endpoints
    path('api/messages/create/', views.MessageCreateView.as_view(), name='message_create'),
    path('api/messages/<uuid:message_id>/delete/', views.MessageDeleteView.as_view(), name='message_delete'),
    path('api/messages/<uuid:message_id>/restore/', views.MessageRestoreView.as_view(), name='message_restore'),
    path('api/messages/<uuid:message_id>/mark-read/', views.MessageMarkReadView.as_view(), name='message_mark_read'),
    path('api/messages/<uuid:message_id>/toggle-star/', views.MessageToggleStarView.as_view(),
         name='message_toggle_star'),
    path('api/messages/<uuid:message_id>/add-to-dir/', views.AddToDirectoryView.as_view(), name='add_to_directory'),
    path('mass-mail/<int:campaign_id>/cancel/', views.MassMailCampaignCancelView.as_view(), name='mass_mail_cancel'),
    # Вспомогательные API
    path('api/users/', views.GetUsersListView.as_view(), name='get_users_list'),
    path('api/directories/create/', views.CreateDirectoryView.as_view(), name='create_directory'),
    # Массовая рассылка
    path('mass-mail/', views.MassMailCampaignListView.as_view(), name='mass_mail_list'),
    path('mass-mail/create/', views.MassMailCampaignCreateView.as_view(), name='mass_mail_create'),
    path('mass-mail/<int:campaign_id>/', views.MassMailCampaignDetailView.as_view(), name='mass_mail_detail'),
    path('mass-mail/<int:campaign_id>/edit/', views.MassMailCampaignEditView.as_view(), name='mass_mail_edit'),
    path('mass-mail/<int:campaign_id>/send/', views.MassMailCampaignSendView.as_view(), name='mass_mail_send'),
    path('mass-mail/<int:campaign_id>/delete/', views.MassMailCampaignDeleteView.as_view(), name='mass_mail_delete'),

    # Настройки
    path('settings/', views.MailSettingsModerationView.as_view(), name='mail_settings'),
    path('settings/test-connection/', views.test_smtp_connection, name='test_smtp_connection'),

]